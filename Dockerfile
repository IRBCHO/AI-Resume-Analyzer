# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy the Lambda function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the Lambda handler
CMD ["lambda_function.lambda_handler"]
