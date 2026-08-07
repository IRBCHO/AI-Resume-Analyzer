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

    prompt = f"""You are a career coach, senior technical recruiter, and ATS expert helping a job seeker improve their application.
Analyze the resume against the job description and provide actionable, specific guidance.

Return ONLY a raw JSON object (no markdown, no backticks, start with {{ and end with }}) with ALL of these keys:

1. "score": integer 0-100 overall match percentage
2. "verdict": one of "Strong Match", "Good Match", "Partial Match", or "Not a Match"
3. "summary": 2-3 sentence executive summary written directly TO the job seeker (use "you/your")
4. "strengths": array of 4-5 specific strengths that align with the role
5. "gaps": array of 3-5 specific skill or experience gaps
6. "suggestions": array of 4-5 actionable improvement suggestions the job seeker can do THIS WEEK
7. "keywords": object with:
   - "matched": array of keywords/skills from the JD found in the resume
   - "missing": array of important keywords/skills from the JD NOT in the resume
8. "ats_score": integer 0-100 for ATS compatibility
9. "ats_tips": array of 3-4 specific ATS improvement tips
10. "experience_alignment": object with:
    - "years_expected": string (or "Not specified")
    - "years_detected": string (or "Unable to determine")
    - "assessment": one sentence assessment
11. "section_scores": object with integer scores 0-100:
    - "skills", "experience", "education", "overall_presentation"
12. "rewritten_bullets": array of 3 objects, each with:
    - "original": a weak bullet point from the resume (or "N/A" if resume has no bullets)
    - "improved": a rewritten version using strong action verbs and quantified results
    - "why": one sentence explaining why the improvement is better
13. "tailored_summary": a 2-3 sentence professional summary rewritten specifically for this job
14. "interview_prep": object with:
    - "likely_questions": array of 3 questions the interviewer will likely ask based on the JD
    - "talking_points": array of 3 things from the resume the candidate should emphasize
    - "red_flags": array of 1-2 potential concerns the interviewer might raise
15. "next_steps": array of 3 specific, prioritized actions the job seeker should take right now (most impactful first)

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}"""

    bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    req = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    })

    try:
        resp = bedrock.invoke_model(modelId='us.anthropic.claude-sonnet-4-20250514-v1:0', body=req)
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
