from pytubefix import YouTube

url = 'https://www.youtube.com/watch?v=yxPR26rRwxY'

yt = YouTube(url)

stream = yt.streams.get_highest_resolution()

stream.download(r"C:\Users\Administrador\Desktop\System\Downloads YT")

print("Download completo.")