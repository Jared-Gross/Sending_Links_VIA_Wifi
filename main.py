import socket

is_server = False


class Server:
    def __init__(self):
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
            print("Message from: " + str(addr))
            print("From connected user: " + data)
            data = data.upper()
            print("Sending: " + data)
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

        message = input("-> ")
        while message != 'q':
            s.sendto(message.encode('utf-8'), server)
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            print("Received from server: " + data)
            message = input("-> ")
        s.close()


if __name__ == '__main__':
    if is_server:
        Server()
    else:
        Client()
