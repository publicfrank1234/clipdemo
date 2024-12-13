import time
import logging
from downloader.youtube import youtube_handler
from downloader.schema import HandlerInput
from processor.vectorizer import vectorize
from processor.weaviate import query_weaviate
from processor.video_processing import create_clip  # Import function to create video clips
from urllib.parse import urlparse, urlunparse

# Configure logging
logging.basicConfig(level=logging.INFO)

def process_video(youtube_url, email, custom_request, job_id):
    """
    Process a video job by downloading, embedding, querying, and creating a clip.

    Args:
        youtube_url (str): The URL of the YouTube video to process.
        email (str): The email address for notification (optional).
        custom_request (str): Any custom request or instructions (optional).
        job_id (str): The unique job ID.
    """
    logging.info(f"Starting job {job_id} for video: {youtube_url}")
    logging.info(f"Custom request: {custom_request if custom_request else 'None'}")

    try:
        # Normalize the video URL to ensure consistency in video_id
        video_id = normalize_url(str(youtube_url))

        # Check if the video is already vectorized in Weaviate
        existing_data = check_if_vectorized(video_id)
        if existing_data:
            logging.info(f"Video {youtube_url} is already vectorized. Skipping vectorization.")
        else:
            # Step 1 - Download YouTube video
            input_request = HandlerInput(
                organization_id="test_organization",
                owner_id=email,
                url=str(youtube_url),
                handler_key="youtube",
            )
            file_resp = youtube_handler(input_request)
            video_path = file_resp.file_data  # Path to downloaded video
            logging.info(f"Video downloaded to {video_path}")

            # Step 2 - Vectorize and save embeddings
            vectorize(video_path, video_id)
            logging.info(f"Embeddings and metadata saved to Weaviate for video: {video_path}")

        # Step 3 - Query relevant frames within the same video
        relevant_frames = query_weaviate(custom_request, video_id, top_k=30)  # Use video_id to filter
        logging.info(f"Relevant frames retrieved: {relevant_frames}")

        # Step 4 - Create a clip
        timestamp_ranges = [(frame["timestamp"] - 2, frame["timestamp"] + 2) for frame in relevant_frames]
        output_clip_path = f"output_clip_{job_id}.mp4"
        create_clip(video_path, timestamp_ranges, output_clip_path)
        logging.info(f"Clip created at: {output_clip_path}")

        # Step 5 - Notify the user
        if email:
            send_email(email, f"Your video {youtube_url} has been processed! Clip available at {output_clip_path}")
        else:
            logging.info("No email provided; skipping notification.")

        logging.info(f"Job {job_id} completed successfully.")

    except Exception as e:
        logging.error(f"Error processing job {job_id}: {e}")


def check_if_vectorized(video_id):
    """
    Check if a video is already vectorized in Weaviate.

    Args:
        video_id (str): The normalized video ID.

    Returns:
        bool: True if the video is vectorized, False otherwise.
    """
    try:
        result = query_weaviate(video_id=video_id, query_input=None, top_k=1)  # Query for the video_id
        return len(result) > 0
    except Exception as e:
        logging.error(f"Error checking vectorization for video_id {video_id}: {e}")
        return False


def send_email(to_email, message):
    """
    Mock function to simulate sending an email.

    Args:
        to_email (str): The recipient's email address.
        message (str): The email message body.
    """
    logging.info(f"Sending email to {to_email}")
    logging.info(f"Message: {message}")
    # Simulated delay for sending an email
    time.sleep(2)
    logging.info(f"Email sent to {to_email}")


def normalize_url(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(scheme=parsed.scheme.lower(), path=parsed.path.rstrip('/')))
