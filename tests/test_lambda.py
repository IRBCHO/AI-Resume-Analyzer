import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import lambda_function
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
    """Valid request with mocked Bedrock should return 200 with analysis key."""
    mock_bedrock = MagicMock()
    mock_boto_client.return_value = mock_bedrock

    # Mock Bedrock response matching the real response structure
    fake_analysis = {
        "score": 85,
        "summary": "Strong candidate with AWS experience.",
        "strengths": ["AWS Lambda", "Python", "Cloud infrastructure"],
        "gaps": ["Kubernetes", "Terraform", "CI/CD experience"],
        "suggestions": ["Learn Terraform", "Get Kubernetes certified", "Build CI/CD projects"],
        "verdict": "Good Match"
    }

    mock_response_body = MagicMock()
    mock_response_body.read.return_value = json.dumps({
        "content": [{"text": json.dumps(fake_analysis)}]
    }).encode()

    mock_bedrock.invoke_model.return_value = {"body": mock_response_body}

    event = make_event(
        resume="Experienced cloud engineer with AWS Lambda and Python skills",
        jd="Looking for a DevOps engineer with AWS and Kubernetes experience"
    )

    response = lambda_function.lambda_handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "analysis" in body
    assert body["analysis"]["score"] == 85
    assert body["analysis"]["verdict"] == "Good Match"
