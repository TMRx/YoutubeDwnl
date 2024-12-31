from pytubefix import YouTube
from pytubefix.cli import on_progress

# add your url video
url = "https://www.youtube.com/watch?v=-zEnxop4Hng"

video = YouTube(
    url=url,
    on_progress_callback=on_progress,  
)


print('Title:', video.title)

stream = video.streams.get_highest_resolution()
stream.download()

print("Download completed!")
