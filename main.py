import socket, os, webbrowser

is_server = False


class Server:
    def __init__(self):
        self.Main()

    def Main(self):
        import psutil
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
            try:
                for p in psutil.process_iter(attrs=['pid', 'name']):
                    if "chrome.exe" in (p.info['name']).lower(): os.system("TASKKILL /F /IM chrome.exe")
            except:
                pass
            webbrowser.open(data)
            print("Playing: " + data)
            s.sendto(data.encode('utf-8'), addr)
        c.close()


class Client:
    def __init__(self):
        self.Main()

    def Main(self):
        host = '10.0.0.215'  # client ip
        port = 4005

        server = ('10.0.0.219', 4000)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))

        message = input("Paste a YT link -> ")
        while message != 'q':
            s.sendto(message.encode('utf-8'), server)
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            print("Currently Playing: " + data)
            message = input("Paste a YT link -> ")
        s.close()


if __name__ == '__main__':
    if is_server:
        Server()
    else:
        Client()
