from pytubefix import YouTube
from pytubefix.cli import on_progress

# Коректний URL відео
url = "https://www.youtube.com/watch?v=-zEnxop4Hng"

# Завантаження відео з використанням YouTube
video = YouTube(
    url=url,
    on_progress_callback=on_progress,  # Виклик прогресу завантаження
)

# Вивід назви відео
print('Title:', video.title)

# Завантаження відео у найвищій доступній якості
stream = video.streams.get_highest_resolution()
stream.download()

print("Download completed!")
