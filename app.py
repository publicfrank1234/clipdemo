from flask import Flask, request, jsonify
import uuid
from flask_cors import CORS
from pydantic import BaseModel, HttpUrl, EmailStr, ValidationError
from typing import Optional
from config import Config  # Import the centralized configuration
import task.tasks as tasks  # Import task processing functions

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Get the RQ queue from the config
queue = Config.get_queue()

# In-memory job store (for now)
jobs = []

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        response = app.response_class(status=204)
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

# Updated JobRequest to include custom_request
class JobRequest(BaseModel):
    youtube_url: HttpUrl
    email: Optional[EmailStr] = None
    custom_request: Optional[str] = None  # Custom request field

@app.route('/create-job', methods=['POST'])
def create_job():
    try:
        # Validate incoming request data
        data = JobRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    # Create a unique job ID
    job_id = str(uuid.uuid4())

    # Enqueue the job in RQ
    job = queue.enqueue(tasks.process_video, data.youtube_url, data.email, data.custom_request, job_id)

    # Store job details in memory for now
    jobs.append({
        "job_id": job_id,
        "youtube_url": data.youtube_url,
        "email": data.email,
        "custom_request": data.custom_request,
        "status": "queued",
    })

    return jsonify({
        "message": "Job created",
        "job_id": job.id,
        "status": job.get_status(),
    })

@app.route('/jobs', methods=['GET'])
def get_jobs():
    return jsonify(jobs)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
