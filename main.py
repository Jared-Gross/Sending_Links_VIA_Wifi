import os
import socket
import subprocess
import threading
import sys
import logging

import pafy
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play


current_platform = ('Linux' if sys.platform in [
                    "linux", "linux2"] else 'Windows')
if current_platform == 'Windows':
    from pynput import keyboard
else:
    try:
        import keyboard
    except ImportError:
        print('Run program in sudo.')

# Declaring server IP and port
server_ip = '10.0.0.219'
server_port = 4000

# Declaring clients IP and port
client_ip = '10.0.0.215'
client_port = 4005

IS_THIS_HOST = True


class Server:
    def __init__(self):
        # Declare variables
        self.DOWNLOAD_FOLDER = os.path.dirname(
            os.path.realpath(__file__)) + '/Downloads/'
        self.currently_playing = False

        # Create music folder if it doesn't exist
        if not os.path.exists(self.DOWNLOAD_FOLDER):
            os.mkdir(self.DOWNLOAD_FOLDER)

        # Start server
        self.Start_Server()

    def Start_Server(self):
        try:
            # Starting server
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((server_ip, server_port))
            print(f"Server Started succesfully on {server_ip}:{server_port}")
        except Exception as e:
            # Server failed to start
            print(f'Server could not start.\n\nReason:\n{e}')
            return
        while True:
            # Wait for message from client
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            print("Message received from: " + str(addr))
            print("Link received: " + data)
            url = [data]

            try:
                # If we recieved a link to a play list, procceed to split up the playlist into YouTube WATCH links
                playlist = pafy.get_playlist(url[0])
                url = []
                for i, j in enumerate(playlist['items']):
                    i_pafy = j['pafy']
                    y_url = i_pafy.watchv_url
                    url.append(y_url)
            except ValueError:
                pass
            # Download and process every youtube link
            for y_url in url:
                logging.basicConfig(filename='Server.log', filemode='a',
                                    format='%(asctime)s - %(message)s', datefmt='%A %B %d %Y %I:%M:%S%p',
                                    level=logging.DEBUG)
                video = pafy.new(y_url)
                logging.info(
                    f'Played: URL: {url}\tTITLE: {video.title}\tAUTHOR: {video.author}')
                # print(video.category)
                s.sendto(
                    f"Found {video.title} - {video.author} - {video.duration}".encode('utf-8'), addr)
                streams = video.streams
                for i in streams:
                    print(i)
                # Get the best audio format for the video/music and download it.
                best = video.getbestaudio()
                name = os.path.splitext(best.filename)[0]
                if video.category == 'Music':
                    if not os.path.exists(f'{self.DOWNLOAD_FOLDER}{video.category}/{video.author}/{name}.mp3'):
                        s.sendto(
                            f"Downloading {video.title} - {video.author} - {video.duration}".encode('utf-8'), addr)
                        best.download()
                else:
                    if not os.path.exists(f'{self.DOWNLOAD_FOLDER}{video.category}/{video.author}/{name}.mp4'):
                        s.sendto(
                            f"Downloading {video.title} - {video.author} - {video.duration}".encode('utf-8'), addr)
                        best.download()
                        # Create a folder for the video author and category if it doesnt exist
                if not os.path.exists(f'{self.DOWNLOAD_FOLDER}{video.category}/'):
                    os.mkdir(
                        f'{self.DOWNLOAD_FOLDER}{video.category}/')
                if not os.path.exists(f'{self.DOWNLOAD_FOLDER}{video.category}/{video.author}/'):
                    os.mkdir(
                        f'{self.DOWNLOAD_FOLDER}{video.category}/{video.author}/')

                s.sendto(
                    f"Converting {video.title} - {video.author} - {video.duration}".encode('utf-8'), addr)
                if video.category == 'Music':
                    # Convert the audio to .mp3 format and move it video author folder
                    subprocess.call(["ffmpeg", "-i", f'{os.path.dirname(os.path.realpath(__file__))}/{best.filename}', '-vn',
                                     '-ar', '44100', '-ac', '2', '-b:a', '192k', f'{self.DOWNLOAD_FOLDER}{video.category}/{video.author}/{name}.mp3', '-n'])
                else:
                    # Convert the video to .mp4 format and move it video author folder
                    subprocess.call(["ffmpeg", "-i", f'{os.path.dirname(os.path.realpath(__file__))}/{best.filename}',
                                     '-ar', '44100', '-ac', '2', '-b:a', '192k', f'{self.DOWNLOAD_FOLDER}{video.category}/{video.author}/{name}.mp4', '-n'])
                # Delete the downloaded file, as we don't need it anymore.
                try:
                    os.remove(
                        f'{os.path.dirname(os.path.realpath(__file__))}/{best.filename}')
                except FileNotFoundError:
                    pass
                s.sendto(
                    f"Playing {video.title} - {video.author} - {video.duration}".encode('utf-8'), addr)

                # Play the .mp3 audio file.
                # TODO rewrite this to work with VLC
                if current_platform == 'Windows':
                    playsound(
                        f"{self.DOWNLOAD_FOLDER}{video.category}/{video.author}/{name}.mp3")
                else:
                    music = AudioSegment.from_mp3(
                        f"{self.DOWNLOAD_FOLDER}{video.category}/{video.author}/{name}.mp3")
                    play(music)
        c.close()


class Client:
    def __init__(self):
        # if current_platform == 'Windows':
        #     listener = keyboard.Listener(on_press=self.on_press_Windows)
        #     listener.start()  # start to listen on a separate thread
        #     listener.join()  # remove if main thread is polling self.keys
        # else:
        #     threading.Thread(target=self.on_press_Linux()).start()
        self.Main()

    def Main(self):
        server = (server_ip, server_port)  # server ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((client_ip, client_port))
        os.system(f'ping {server_ip}')

        message = input("Paste a YT link -> ")
        while message != 'q':
            s.sendto(message.encode('utf-8'), server)
            data, addr = s.recvfrom(1024).decode('utf-8')
            if data != '':
                print(data)
            data, addr = s.recvfrom(1024).decode('utf-8')
            if data != '':
                print(data)
            data, addr = s.recvfrom(1024).decode('utf-8')
            if data != '':
                print(data)
            data, addr = s.recvfrom(1024).decode('utf-8')
            print(data)
            message = input("Paste a YT link -> ")
        s.close()

    def on_press_Windows(self, key):
        # if key == keyboard.Key.esc:
        #     return False  # stop listener
        try:
            k = key.char  # single-char keys
        except:
            k = key.name  # other keys
        print('Key pressed: ' + str(k))
        # if k in ['1', '2', 'left', 'right']:  # keys of interest
        # self.keys.append(k)  # store it in global-like variable

    def on_press_Linux(self):
        while True:
            if keyboard.read_key() == "f13":
                print("volume mute")
            elif keyboard.read_key() == "help":
                print("volume up")
            elif keyboard.read_key() == "f14":
                print("volume down")


if __name__ == '__main__':
    if IS_THIS_HOST:
        Server()
    else:
        Client()
