# Dockerfile

FROM python:3.11-slim
WORKDIR /usr/src/app

# Copy dependency file first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all our application code
COPY ./app ./app
COPY run.py .
# If you created it
COPY apidocs.yaml . 

ENV DOCUMENT_ROOT=/data

# Run the application using the new runner script
CMD ["python", "run.py"]