import json
import boto3


def lambda_handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': ''
        }

    try:
        body = json.loads(event.get('body', '{}'))
        resume_text = body.get('resume', '').strip()
        jd_text = body.get('jd', '').strip()
    except Exception:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid request body.'})
        }

    if not resume_text or not jd_text:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Resume and job description required'})
        }

    prompt = build_prompt(resume_text, jd_text)

    bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    req = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    })

    try:
        resp = bedrock.invoke_model(
            modelId='us.anthropic.claude-sonnet-4-6', body=req
        )
        raw_text = json.loads(resp.get('body').read())['content'][0]['text']

        cleaned = raw_text.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned.split('\n', 1)[1] if '\n' in cleaned else cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3].strip()

        analysis = json.loads(cleaned)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'analysis': analysis})
        }
    except json.JSONDecodeError as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Failed to parse AI response: {str(e)}'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


def build_prompt(resume_text, jd_text):
    schema = (
        '{"score":int,"verdict":"Strong Match|Good Match|Partial Match|Not a Match",'
        '"summary":"2 sentences to job seeker",'
        '"strengths":["3 items"],"gaps":["3 items"],"suggestions":["3 tips"],'
        '"keywords":{"matched":[],"missing":[]},'
        '"ats_score":int,"ats_tips":["3 tips"],'
        '"section_scores":{"skills":int,"experience":int,"education":int,"overall_presentation":int},'
        '"rewritten_bullets":[{"original":"","improved":"","why":""}],'
        '"tailored_summary":"2 sentence summary for this job",'
        '"interview_prep":{"likely_questions":["2"],"talking_points":["2"],"red_flags":["1"]},'
        '"next_steps":["3 prioritized actions"]}'
    )

    return (
        "You are a career coach. Analyze the resume against the job description. "
        "Be concise and direct. Address the job seeker as 'you'.\n\n"
        "Return ONLY a JSON object matching this schema (no markdown, no backticks):\n"
        f"{schema}\n\n"
        f"RESUME:\n{resume_text}\n\n"
        f"JOB DESCRIPTION:\n{jd_text}"
    )
