from task.tasks import process_video

# Test the process_video function
process_video(
    youtube_url="https://www.youtube.com/watch?v=example",
    email="test@example.com",
    custom_request="Process in HD",
    job_id="test-job-123"
)
