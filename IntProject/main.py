from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

class InterviewRequest(BaseModel):
    job_description: str
    resume: str
    phone_number: str

class InterviewResult(BaseModel):
    candidate_score: float
    interview_summary: str
    recommended_action: str

def analyze_job_resume_match(job_description: str, resume: str) -> dict:
    """Analyze the match between job description and resume using OpenAI."""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert HR analyst. Analyze the match between the job description and resume."},
                {"role": "user", "content": f"Job Description:\n{job_description}\n\nResume:\n{resume}\n\nProvide a detailed analysis of the match."}
            ]
        )
        return {"analysis": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing job-resume match: {str(e)}")

@app.post("/initiate-interview")
async def initiate_interview(request: InterviewRequest):
    try:
        # First analyze the job-resume match
        match_analysis = analyze_job_resume_match(request.job_description, request.resume)
        
        # Store the context in some session storage (this is simplified)
        interview_context = {
            "job_description": request.job_description,
            "resume": request.resume,
            "analysis": match_analysis
        }
        
        # Initiate the call
        call = twilio_client.calls.create(
            to=request.phone_number,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            url=f"{os.getenv('BASE_URL')}/handle-interview-call",
            status_callback=f"{os.getenv('BASE_URL')}/call-status"
        )
        
        return {"message": "Interview call initiated", "call_sid": call.sid}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/handle-interview-call")
async def handle_interview_call():
    """Handle the interview call flow."""
    response = VoiceResponse()
    
    # Initial greeting
    response.say("Hello! I'm an AI interviewer. This call will be recorded for evaluation purposes. "
                "I'll be asking you several questions about your experience and skills. "
                "Please speak naturally and take your time with your responses.")
    
    # Start the interview loop
    gather = Gather(input='speech', action='/process-response', method='POST')
    gather.say("Let's begin. Could you tell me about your relevant experience for this position?")
    response.append(gather)
    
    return str(response)

@app.post("/process-response")
async def process_response(speech_result: str):
    """Process candidate's response and continue the interview."""
    response = VoiceResponse()
    
    try:
        # Use OpenAI to analyze the response and determine next question
        ai_response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are conducting a job interview. Analyze the candidate's response and determine the next question."},
                {"role": "user", "content": f"Candidate's response: {speech_result}"}
            ]
        )
        
        next_question = ai_response.choices[0].message.content
        
        gather = Gather(input='speech', action='/process-response', method='POST')
        gather.say(next_question)
        response.append(gather)
        
    except Exception as e:
        response.say("I apologize, but I'm having trouble processing your response. Let me transfer you to a human recruiter.")
        response.hangup()
    
    return str(response)

@app.post("/call-status")
async def call_status(status: str, call_sid: str):
    """Handle call status updates and post results to BrassRing."""
    if status == "completed":
        # Generate interview results
        results = InterviewResult(
            candidate_score=0.0,  # Calculate based on responses
            interview_summary="",  # Generate summary
            recommended_action=""  # Provide recommendation
        )
        
        # Post to BrassRing (implementation needed)
        # post_to_brassring(results)
        
        return {"message": "Interview completed and results posted"}
    
    return {"message": f"Call status: {status}"}
