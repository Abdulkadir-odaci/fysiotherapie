import os
import subprocess
import glob

def create_preview_videos(input_folder, output_folder=None, preview_duration=4):
    """
    Create preview videos for all MP4 files in the input folder.
    
    Args:
        input_folder (str): Path to the folder containing the original videos
        output_folder (str, optional): Path to save the preview videos. If None, uses input_folder
        preview_duration (int, optional): Duration of preview videos in seconds
    """
    # If no output folder is specified, use the input folder
    if output_folder is None:
        output_folder = input_folder
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all MP4 files in the input folder
    video_files = glob.glob(os.path.join(input_folder, "*.mp4"))
    
    print(f"Found {len(video_files)} video files to process.")
    
    for video_path in video_files:
        # Get the base filename without extension
        basename = os.path.basename(video_path)
        name_without_ext = os.path.splitext(basename)[0]
        
        # Create output filename
        output_filename = f"{name_without_ext}_preview.mp4"
        output_path = os.path.join(output_folder, output_filename)
        
        # FFmpeg command to create a 4-second preview
        # -ss 00:00:01: start at 1 second to avoid black frames
        # -t 00:00:04: take 4 seconds of video
        # -c:v libx264: encode with H.264 codec
        # -crf 23: set quality (lower is better)
        # -preset fast: balance between encoding speed and compression
        # -c:a aac: encode audio with AAC codec
        # -b:a 128k: audio bitrate
        # -vf scale=640:-1: resize to 640px width, keeping aspect ratio
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", "00:00:01",
            "-t", f"00:00:0{preview_duration}",
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "128k",
            "-vf", "scale=640:-1",
            "-y",  # Overwrite output files without asking
            output_path
        ]
        
        print(f"Creating preview for {basename}...")
        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully created {output_filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating preview for {basename}: {e}")

if __name__ == "__main__":
    # Change these paths to match your setup
    videos_folder = r"C:\Users\abdlk\Desktop\fysiotherapie\videos"  # Path to your videos folder
    
    # Create preview videos in the same folder
    create_preview_videos(videos_folder)
    
    print("All preview videos created successfully!")