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
            'body': json.dumps({'error': 'Invalid request body. Please send valid JSON.'})
        }

    if not resume_text or not jd_text:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Resume and job description required'})
        }

    prompt = f"""You are a senior technical recruiter and ATS (Applicant Tracking System) expert.
Analyze the following resume against the job description with extreme detail.

Return ONLY a raw JSON object (no markdown, no backticks, start with {{ and end with }}) with these keys:

1. "score": integer 0-100 representing overall match percentage
2. "verdict": one of "Strong Match", "Good Match", "Partial Match", or "Not a Match"
3. "summary": 2-3 sentence executive summary of the candidate's fit
4. "strengths": array of 4-5 specific strengths the candidate has that align with the role
5. "gaps": array of 3-5 specific skill or experience gaps
6. "suggestions": array of 4-5 actionable improvement suggestions
7. "keywords": object with two keys:
   - "matched": array of keywords/skills from the JD found in the resume
   - "missing": array of important keywords/skills from the JD NOT found in the resume
8. "ats_score": integer 0-100 representing how well the resume would pass an ATS scan for this role
9. "ats_tips": array of 3-4 specific tips to improve ATS compatibility
10. "experience_alignment": object with:
    - "years_expected": string of years expected from JD (or "Not specified")
    - "years_detected": string of approximate years detected in resume (or "Unable to determine")
    - "assessment": one sentence assessment of experience level fit
11. "section_scores": object with scores (0-100) for each resume section:
    - "skills": integer score for technical skills match
    - "experience": integer score for work experience relevance
    - "education": integer score for education fit
    - "overall_presentation": integer score for resume formatting/clarity

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}"""

    bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    req = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 3000,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    })

    try:
        resp = bedrock.invoke_model(modelId='us.anthropic.claude-sonnet-4-5-20250514', body=req)
        raw_text = json.loads(resp.get('body').read())['content'][0]['text']

        # Clean response - strip any accidental markdown wrapping
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
