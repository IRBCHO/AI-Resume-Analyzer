import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import lambda_function


def make_event(resume="", jd="", method="POST"):
    return {
        "httpMethod": method,
        "body": json.dumps({"resume": resume, "jd": jd})
    }


def test_options_request_returns_200():
    """CORS preflight request should return 200."""
    event = {"httpMethod": "OPTIONS"}
    response = lambda_function.lambda_handler(event, None)
    assert response["statusCode"] == 200


def test_missing_resume_returns_400():
    """Request with empty resume should return 400."""
    event = make_event(resume="", jd="Software Engineer role")
    response = lambda_function.lambda_handler(event, None)
    assert response["statusCode"] == 400


def test_missing_jd_returns_400():
    """Request with empty job description should return 400."""
    event = make_event(resume="I am a cloud engineer", jd="")
    response = lambda_function.lambda_handler(event, None)
    assert response["statusCode"] == 400


def test_invalid_json_returns_400():
    """Malformed JSON body should return 400."""
    event = {"httpMethod": "POST", "body": "not-valid-json"}
    response = lambda_function.lambda_handler(event, None)
    assert response["statusCode"] == 400


@patch("lambda_function.boto3.client")
def test_valid_request_returns_200(mock_boto_client):
    """Valid request with mocked Bedrock returns full analysis."""
    mock_bedrock = MagicMock()
    mock_boto_client.return_value = mock_bedrock

    fake_analysis = {
        "score": 85,
        "verdict": "Good Match",
        "summary": "Strong candidate with AWS experience.",
        "strengths": ["AWS Lambda", "Python", "Cloud infra", "CI/CD"],
        "gaps": ["Kubernetes", "Terraform", "On-call"],
        "suggestions": ["Learn Terraform", "Get K8s cert", "Add metrics", "Quantify impact"],
        "keywords": {"matched": ["AWS", "Python"], "missing": ["Kubernetes", "Terraform"]},
        "ats_score": 72,
        "ats_tips": ["Add keywords", "Use standard headings", "Remove graphics"],
        "experience_alignment": {
            "years_expected": "3-5 years",
            "years_detected": "4 years",
            "assessment": "Good fit."
        },
        "section_scores": {"skills": 80, "experience": 85, "education": 70, "overall_presentation": 75}
    }

    mock_response_body = MagicMock()
    mock_response_body.read.return_value = json.dumps({
        "content": [{"text": json.dumps(fake_analysis)}]
    }).encode()
    mock_bedrock.invoke_model.return_value = {"body": mock_response_body}

    event = make_event(
        resume="Experienced cloud engineer with AWS Lambda and Python",
        jd="Looking for a DevOps engineer with AWS and Kubernetes"
    )

    response = lambda_function.lambda_handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "analysis" in body
    assert body["analysis"]["score"] == 85
    assert body["analysis"]["ats_score"] == 72
    assert "matched" in body["analysis"]["keywords"]


@patch("lambda_function.boto3.client")
def test_markdown_wrapped_response(mock_boto_client):
    """Response wrapped in markdown fences should still parse."""
    mock_bedrock = MagicMock()
    mock_boto_client.return_value = mock_bedrock

    fake = {"score": 60, "verdict": "Partial Match", "summary": "Decent.", "strengths": ["Python"], "gaps": ["AWS"], "suggestions": ["Learn AWS"], "keywords": {"matched": ["Python"], "missing": ["AWS"]}, "ats_score": 55, "ats_tips": ["Add keywords"], "experience_alignment": {"years_expected": "2", "years_detected": "1", "assessment": "Under."}, "section_scores": {"skills": 60, "experience": 55, "education": 70, "overall_presentation": 65}}

    wrapped = "```json\n" + json.dumps(fake) + "\n```"
    mock_response_body = MagicMock()
    mock_response_body.read.return_value = json.dumps({"content": [{"text": wrapped}]}).encode()
    mock_bedrock.invoke_model.return_value = {"body": mock_response_body}

    event = make_event(resume="Python dev", jd="AWS engineer needed")
    response = lambda_function.lambda_handler(event, None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["analysis"]["score"] == 60
