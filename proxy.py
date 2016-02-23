import sys
import socket
import threading

def website_blocked(website):
    with open ('blocklist.txt', 'r') as blocklist:
        for line in blocklist:
            print(line)
            if website in line:
                return True
    return False

def proxy_thread(clientsocket, address):
    print("Started a thread")
    ip, port = address
    print("Client IP:", ip, "Port:", port)
    request = clientsocket.recv(4096).decode()
    print(request)

    website = 'thing'
    response = 'This is passing through the proxy'
    if website_blocked(website):
        response = website + ' is blocked by the proxy'

    clientsocket.send(response.encode())
    clientsocket.close()

def main():
    print(sys.argv)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 8080))
    s.listen(5)

    while True:
        (clientsocket, address) = s.accept()
        threading.Thread(target=proxy_thread, args=(clientsocket, address)).start()
    s.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping server...")
        sys.exit(1)
