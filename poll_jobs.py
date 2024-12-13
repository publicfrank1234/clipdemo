import time
from config import Config

# Get the RQ queue from the Config
queue = Config.get_queue()

def process_job(job):
    """
    Process a single job.
    """
    try:
        print(f"Processing job: {job.id}")
        job.perform()  # Execute the job's function
        # job.delete()   # Remove the job from the queue after successful execution
        print(f"Job {job.id} processed successfully.")
    except Exception as e:
        print(f"Error processing job {job.id}: {e}")

def poll_jobs():
    """
    Periodically poll the queue for jobs and process them.
    """
    while True:
        print("Checking the queue for jobs...")
        jobs = queue.jobs  # Get all jobs currently in the queue
        if jobs:
            for job in jobs:
                process_job(job)  # Process each job
        else:
            print("No jobs found. Sleeping for 5 seconds...")
            time.sleep(5)  # Sleep before checking the queue again

if __name__ == "__main__":
    poll_jobs()
