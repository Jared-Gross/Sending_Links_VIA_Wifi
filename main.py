import os
import socket
import subprocess
import threading
import sys

import pafy
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play

is_server = False

current_platform = ('Linux' if sys.platform in ["linux", "linux2"] else 'Windows')
if current_platform == 'Windows':
    from pynput import keyboard
else:
    try:
        import keyboard
    except ImportError:
        print('Run program in sudo.')

class Server:
    def __init__(self):
        self.Music_Folder = os.path.dirname(os.path.realpath(__file__)) + '/Music/'
        self.currently_playing = False
        if not os.path.exists(self.Music_Folder):
            os.mkdir(self.Music_Folder)
        self.Main()
    def Main(self):
        host = '10.0.0.219'  # Server ip
        port = 4000

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))

        print("Server Started")
        while True:
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            print("Message received from: " + str(addr))
            print("Link received: " + data)
            url = data
            video = pafy.new(url)
            streams = video.streams
            for i in streams:print(i)
            best = video.getbestaudio()
            s.sendto(f"Downloading {video.title} - {video.author} - {video.duration}".encode('utf-8'), addr)

            best.download()
            name = os.path.splitext(best.filename)[0]
            if not os.path.exists(self.Music_Folder + video.author + '/'):
                os.mkdir(self.Music_Folder + video.author + '/')
            subprocess.call(["ffmpeg", "-i", f'{os.path.dirname(os.path.realpath(__file__))}/{best.filename}', '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', f'{self.Music_Folder}{video.author}/{name}.mp3', '-n'])
            s.sendto(f"Playing {video.title} - {video.author} - {video.duration}".encode('utf-8'), addr)
            if current_platform == 'Windows':
                playsound(f"{self.Music_Folder}{video.author}/{name}.mp3")
            else:
                music = AudioSegment.from_mp3(f"{self.Music_Folder}{video.author}/{name}.mp3")
                play(music)
        c.close()


class Client:
    def __init__(self):
        if current_platform == 'Windows':
            listener = keyboard.Listener(on_press=self.on_press_Windows)
            listener.start()  # start to listen on a separate thread
            listener.join()  # remove if main thread is polling self.keys
        else:
            threading.Thread(target=self.on_press_Linux()).start()
        self.Main()

    def Main(self):
        host = '10.0.0.215'  # client ip
        port = 4005

        server = ('10.0.0.219', 4000) # server ip

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))

        message = input("Paste a YT link -> ")
        while message != 'q':
            s.sendto(message.encode('utf-8'), server)
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            if data != '': print(data)
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            print(data)
            message = input("Paste a YT link -> ")
        s.close()


    def on_press_Windows(self, key):
        # if key == keyboard.Key.esc:
        #     return False  # stop listener
        try: k = key.char  # single-char keys
        except: k = key.name  # other keys
        print('Key pressed: ' + str(k))
        # if k in ['1', '2', 'left', 'right']:  # keys of interest
        # self.keys.append(k)  # store it in global-like variable
    def on_press_Linux(self):
        while True:
            if keyboard.read_key() == "f13": print("volume mute")
            elif keyboard.read_key() == "help": print("volume up")
            elif keyboard.read_key() == "f14": print("volume down")


if __name__ == '__main__':
    if is_server:
        Server()
    else:
        Client()
