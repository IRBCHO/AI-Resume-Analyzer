# AI Resume Analyzer — CI/CD Pipeline with Docker and AWS

![Build Status](https://github.com/IRBCHO/AI-Resume-Analyzer/actions/workflows/deploy.yml/badge.svg)

A serverless AI-powered resume analyzer built on AWS, with a full 3-stage CI/CD pipeline using GitHub Actions, Docker, and Amazon ECR.

Every push to `main` automatically runs tests, builds a Docker container, pushes it to ECR, and deploys it to AWS Lambda.

---

## What It Does

Paste your resume and a job description. The app uses Amazon Bedrock (Claude) to return:
- Match score (0-100)
- Strengths
- Skill gaps
- Improvement suggestions
- Verdict (Strong Match, Good Match, Partial Match, or Not a Match)

Live demo: [irbcho.github.io/AI-Resume-Analyzer](https://irbcho.github.io/AI-Resume-Analyzer/)

---

## Architecture

```
GitHub Push
    |
    v
GitHub Actions CI/CD Pipeline
    |
    |-- Job 1: Run Tests (pytest)
    |
    |-- Job 2: Build Docker Image --> Push to Amazon ECR
    |
    |-- Job 3: Deploy Container Image --> AWS Lambda
                                              |
                                        API Gateway
                                              |
                                     Amazon Bedrock (Claude)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Amazon Bedrock (Claude Sonnet) |
| Compute | AWS Lambda (Container Image) |
| Container Registry | Amazon ECR |
| API | Amazon API Gateway |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Testing | pytest |
| IaC | AWS IAM, ECR, Lambda via CLI |

---

## CI/CD Pipeline

The pipeline has 3 jobs that run in sequence on every push to `main`.

### Job 1 — Run Tests
Installs dependencies and runs 5 unit tests using pytest. If any test fails, the pipeline stops and nothing gets deployed.

Tests cover:
- CORS preflight (OPTIONS) request handling
- Missing resume input validation
- Missing job description input validation
- Invalid JSON body handling
- Full valid request with mocked Bedrock response

### Job 2 — Build and Push to ECR
Builds a Docker image using the AWS Lambda Python 3.12 base image, tags it with the Git commit SHA for traceability, and pushes it to Amazon ECR. Also tags the image as `latest`.

### Job 3 — Deploy to Lambda
Updates the Lambda function to run the new container image from ECR, waits for the update to complete, and verifies the deployment.

---

## Screenshots

### Pipeline Running — All 3 Jobs Green
![CI/CD Pipeline Success](screenshots/pipeline-success.png)

### All Workflow Runs Passing
![GitHub Actions Runs](screenshots/actions-runs.png)

### Docker Image in Amazon ECR
![ECR Repository](screenshots/ecr-repository.png)

### Lambda Function — Package Type: Image
![Lambda Image](screenshots/lambda-image.png)

---

## Project Structure

```
AI-Resume-Analyzer/
├── .github/
│   └── workflows/
│       └── deploy.yml        # CI/CD pipeline definition
├── tests/
│   └── test_lambda.py        # Unit tests
├── Dockerfile                # Container image definition
├── lambda_function.py        # Lambda handler
├── requirements.txt          # Python dependencies
├── index.html                # Frontend
└── README.md
```

---

## How to Set This Up

### Prerequisites
- AWS account
- GitHub repository
- Docker installed locally
- AWS CLI configured

### Step 1 — Create ECR Repository

Go to AWS Console → ECR → Create repository.

Set the name to `resume-analyzer` and leave all other settings as default.

Copy the repository URI. You will need it in Step 4.

### Step 2 — Create IAM User for GitHub Actions

Go to AWS Console → IAM → Users → Create user.

Name it `GitHubActionsDeployer` and attach these policies:
- `AmazonEC2ContainerRegistryPowerUser`
- `AWSLambda_FullAccess`

Generate an access key and copy the Access Key ID and Secret Access Key.

### Step 3 — Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret.

Add these two secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Step 4 — Create Lambda Function as Container Image

Go to AWS Console → Lambda → Create function → Container image.

Set the function name to `ResumeAnalyzer` and browse ECR to select your `resume-analyzer` repository. After creating, go to Configuration → Permissions and attach an IAM role with Bedrock access.

### Step 5 — Push to GitHub

```bash
git add .
git commit -m "Initial CI/CD pipeline setup"
git push origin main
```

Go to the Actions tab and watch all 3 jobs turn green.

---

## What I Learned

- How to containerize a Lambda function using Docker and the AWS Lambda Python base image
- How to push container images to Amazon ECR using GitHub Actions
- How to write unit tests with pytest and mock AWS SDK calls
- How to structure a multi-job CI/CD pipeline where each stage depends on the previous one
- How to manage IAM permissions for automated deployments
- The difference between Lambda Zip deployment and Container Image deployment

---

## Author

Irene Cho — [LinkedIn](https://www.linkedin.com/in/irene-b-c) | [Portfolio](https://irbcho.github.io/professionalhub/) | [GitHub](https://github.com/IRBCHO)

