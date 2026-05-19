![Build Status](https://github.com/IRBCHO/AI-Resume-Analyzer/actions/workflows/deploy.yml/badge.svg)

# AI Resume Analyzer (AWS Bedrock + DevOps)
# AI Resume Analyzer (AWS Bedrock + DevOps)

This project is an AI-powered resume analyzer that compares a resume with a target job description and gives feedback like strengths, skill gaps, and suggestions for improvement.

I’m building this to practice real-world cloud + DevOps skills while also exploring how AI (Amazon Bedrock) can be used in practical applications.



## Why I built this

As someone transitioning into cloud/DevOps, I wanted a project that:
- solves a real problem (job search)
- uses AWS services in a realistic way
- includes CI/CD and not just basic deployment
- touches AI since it’s becoming important in cloud roles


## What it does

- Takes a resume + job description
- Uses AI (Bedrock) to analyze it
- Returns:
  - summary
  - strengths
  - skill gaps
  - improvement suggestions



## Tech stack

- AWS Lambda (Python)
- Amazon Bedrock
- API Gateway
- S3 (for storage)
- CloudWatch (logs)
- GitHub Actions (CI/CD)



## Architecture

```mermaid
graph LR
    User((User)) -->|Uploads Resume| API[API Gateway]
    API --> Lambda[AWS Lambda<br/>Python Logic]
    Lambda --> Bedrock[Amazon Bedrock<br/>Claude 3.5 Sonnet]
    Lambda --> S3[(S3 Storage)]
    Lambda --> Result[Analysis Report]



## What I’m focusing on

- writing clean backend logic
- setting up CI/CD properly
- learning more about IAM/security
- making the project look like something used in real companies



## Status

Core Backend & Bedrock Integration Complete. Github Actions CI/CD pipeline fully operational.


## Next steps

Right now I’m focused on getting the backend working properly and connecting the app to Amazon Bedrock.

After that, I want to improve the output format, add storage with S3. Once the core functionality is stable, I’d like to support PDF uploads, build a simple frontend, and eventually manage the infrastructure with Terraform.
