import os
from pytubefix import YouTube
from pytubefix.cli import on_progress

# your youTube video URL to download
url = "https://www.youtube.com/watch?v=-zEnxop4Hng"


def combine(audio: str, video: str, output: str) -> None:
    """
    Combines audio and video files into one file using ffmpeg.

    :param audio: Path to the audio file
    :param video: Path to the video file
    :param output: Path to the output file
    """
    if os.path.exists(output):
        os.remove(output)

    code = os.system(f'ffmpeg -i "{video}" -i "{audio}" -c copy "{output}"')

    if code != 0:
        print(f"Error combining audio and video. ffmpeg exit code: {code}")
        raise SystemError(code)


def download(url: str):
    """
    Downloads the video and audio from YouTube based on the provided URL and combines them into one file.

    :param url: YouTube video URL
    """
    try:
        yt = YouTube(
            proxies={"http": "http://127.0.0.1:8881",  
                     "https": "http://127.0.0.1:8881"},
            url=url,
            on_progress_callback=on_progress, 
        )


        video_stream = yt.streams.filter(type='video').order_by('resolution').desc().first()


        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

        print('Information:')
        print(f"\tTitle: {yt.title}")
        print(f"\tAuthor: {yt.author}")
        print(f"\tDate: {yt.publish_date}")
        print(f"\tResolution: {video_stream.resolution}")
        print(f"\tViews: {yt.views}")
        print(f"\tLength: {round(yt.length / 60)} minutes")
        print(f"\tFilename of the video: {video_stream.default_filename}")
        print(f"\tFilesize of the video: {round(video_stream.filesize / 1000000)} MB")

        print('Downloading video...')
        video_stream.download()


        print('Downloading audio...')
        audio_stream.download()

        combine(audio_stream.default_filename, video_stream.default_filename, f'{yt.title}.mp4')

    except Exception as e:
        
        print(f"An error occurred: {e}")

download(url)
