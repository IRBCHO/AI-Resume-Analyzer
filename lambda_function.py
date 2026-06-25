import json
import boto3

def lambda_handler(event, context):

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'POST,OPTIONS'}, 'body': ''}

    try:
        body = json.loads(event.get('body', '{}'))
        resume_text = body.get('resume', '').strip()
        jd_text = body.get('jd', '').strip()
    except Exception:
        return {'statusCode': 400, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': 'Invalid request'})}

    if not resume_text or not jd_text:
        return {'statusCode': 400, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': 'Resume and job description required'})}

    parts = [
        'You are an expert recruiter. Analyze the resume against the job description.',
        'Return ONLY a raw JSON object with these keys:',
        'score (0-100), summary (2 sentences), strengths (list of 3),',
        'gaps (list of 3), suggestions (list of 3),',
        'verdict (Strong Match or Good Match or Partial Match or Not a Match).',
        'No markdown, no backticks, start with { and end with }.',
        '',
        'RESUME:',
        resume_text,
        '',
        'JOB DESCRIPTION:',
        jd_text
    ]
    prompt = '\n'.join(parts)

    bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    req = json.dumps({"anthropic_version": "bedrock-2023-05-31", "max_tokens": 1500, "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]})

    try:
        resp = bedrock.invoke_model(modelId='us.anthropic.claude-sonnet-4-6', body=req)
        text = json.loads(resp.get('body').read())['content'][0]['text']
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'analysis': json.loads(text)})}
    except Exception as e:
        return {'statusCode': 500, 'headers': {'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': str(e)})}
