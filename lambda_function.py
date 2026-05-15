import json
import boto3

def lambda_handler(event, context):
    # Initialize the Bedrock client
    bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    
    # Get the resume and job description from the test event or API request
    resume_text = event.get('resume', '')
    jd_text = event.get('jd', '')
    
    # Construct the prompt for Claude 4.6
    prompt = f"Analyze this resume against the job description. Provide strengths and gaps.\n\nResume: {resume_text}\n\nJob Description: {jd_text}"
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    })

    try:
        response = bedrock.invoke_model(
            modelId='us.anthropic.claude-sonnet-4-6',
            body=body
        )
        
        response_body = json.loads(response.get('body').read())
        analysis = response_body['content'][0]['text']
        
        return {
            'statusCode': 200,
            'body': json.dumps({'analysis': analysis})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
