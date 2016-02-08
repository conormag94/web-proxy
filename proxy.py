import sys
import socket

def main():
    print(sys.argv)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(5)

    while True:
        (clientsocket, address) = s.accept()
        ip, port = address
        print("Client IP:", ip, "Port:", port)

    s.close()

if __name__ == '__main__':
    main()
