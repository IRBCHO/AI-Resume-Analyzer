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

    prompt = "You are an expert recru
