import cv2
from PIL import Image
from moviepy import VideoFileClip, concatenate_videoclips

def extract_keyframes(video_path, frame_interval=30):
    """
    Extract keyframes and their corresponding timestamps from a video.

    Args:
        video_path (str): Path to the video file.
        frame_interval (int): Number of frames to skip between keyframes.

    Returns:
        tuple: (list of keyframes as PIL Images, list of timestamps in seconds).
    """
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)  # Frames per second
    keyframes = []
    timestamps = []

    success, image = video.read()
    count = 0

    while success:
        if count % frame_interval == 0:
            # Convert frame to PIL Image
            keyframe = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            keyframes.append(keyframe)

            # Calculate and store the timestamp
            timestamp = count / fps
            timestamps.append(timestamp)

        success, image = video.read()
        count += 1

    video.release()
    return keyframes, timestamps


def create_clip(video_path, timestamp_ranges, output_path):
    """
    Create a video clip by extracting specified timestamp ranges.

    Args:
        video_path (str): Path to the source video.
        timestamp_ranges (list of tuples): List of (start, end) timestamps for each segment.
        output_path (str): Path to save the final concatenated video clip.
    """
    video = VideoFileClip(video_path)

    # Extract and concatenate the subclips
    clips = [
        video.subclipped(max(0, start), min(video.duration, end))
        for start, end in timestamp_ranges
    ]
    final_clip = concatenate_videoclips(clips)

    # Write the final video to the specified output path
    final_clip.write_videofile(output_path, codec="libx264")
