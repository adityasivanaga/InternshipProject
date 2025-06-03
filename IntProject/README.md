# AI-Powered Interview System

This system conducts automated phone interviews by analyzing job descriptions and resumes, making phone calls to candidates, and posting results to BrassRing.

## Features

- Job description and resume analysis using GPT-4
- Automated phone interviews using Twilio
- Real-time conversation processing
- Automatic result generation and posting to BrassRing
- Secure handling of sensitive information

## Prerequisites

- Python 3.8+
- OpenAI API key
- Twilio account with:
  - Account SID
  - Auth Token
  - Phone number
- BrassRing API access (for posting results)

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.template` to `.env` and fill in your credentials:
   ```bash
   cp .env.template .env
   ```
4. Edit `.env` with your actual credentials

## Running the Application

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. The API will be available at `http://localhost:8000`

## API Endpoints

### POST /initiate-interview
Initiates an interview with the following parameters:
```json
{
    "job_description": "string",
    "resume": "string",
    "phone_number": "string"
}
```

### POST /handle-interview-call
Webhook endpoint for Twilio to handle the interview flow

### POST /process-response
Processes candidate responses during the interview

### POST /call-status
Handles call status updates and posts results to BrassRing

## Security Considerations

- All API keys and sensitive credentials should be stored in the `.env` file
- The application should be deployed with HTTPS enabled
- Phone numbers should be validated and sanitized
- Rate limiting should be implemented in production

## Production Deployment

1. Deploy to a secure server with HTTPS
2. Set up proper monitoring and logging
3. Configure proper error handling and fallback mechanisms
4. Implement rate limiting
5. Set up proper database for storing interview results

## Error Handling

The system includes fallback mechanisms:
- Automatic transfer to human recruiter if AI processing fails
- Retry mechanisms for failed API calls
- Graceful degradation of services 