import sys
import socket
import threading
import click

# Returns True if there is a already a cached file named fname, False otherwise
def in_cache(fname):
    try:
        f = open(fname, 'rb')
        return True
    except IOError:
        return False

# Returns whether or not website is blocked in the blocklist
def website_blocked(website):
    with open ('blocklist.txt', 'r') as blocklist:
        for line in blocklist:
            if website in line:
                return True
    return False

# Handles a http request which has come in from clientsocket
def proxy_thread(clientsocket, address):

    request = clientsocket.recv(4096).decode()
    print(request)

    first_line = request.split('\n')[0]     # eg: GET http://google.ie
    url = first_line.split(' ')[1]          # eg: http://google.ie or http://www.google.ie
    cached_name = url.replace('/', '')      # stripping awkward characters to make a cached file name

    http_pos = url.find('://')          
    website = url[http_pos+3:]              # eg: google.ie or www.google.ie
    temp = website.replace('www.', '')

    # if there is a trailing slash, don't include it
    slash_pos = temp.find('/')              
    if slash_pos == -1:
        hostname = temp
    else:
        hostname = temp[:slash_pos]
    #print("Host: " + hostname)

    if website_blocked(hostname):
        response = '<h1>' + hostname + ' is blocked by the proxy</h1>'
        clientsocket.send(response.encode())
        clientsocket.close()
    else:
        try:
            # if the site is cached, send client cached version instead of retrieving from server
            if in_cache(cached_name):
                print("[*] Cache hit - Retrieving from cache...")
                f = open(cached_name, 'rb')
                data = f.read(4096)
                while (len(data) > 0):
                    clientsocket.send(data)
                    data = f.read(4096)
                clientsocket.close()
                f.close()
            # if not cached, make a new cache file and fill it with data retrieved from server
            else:
                print("[*] Cache miss - Retrieving from server...")
                f = open(cached_name, 'wb')
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((hostname, 80))
                s.send(request.encode())

                while 1:
                    # receive data from web server
                    data = s.recv(4096)

                    if (len(data) > 0):
                        # send to browser
                        f.write(data)
                        clientsocket.send(data)
                    else:
                        break
                f.close()
                s.close()
                clientsocket.close()
        except socket.error:
            if s:
                s.close()
            if clientsocket:
                clientsocket.close()
            sys.exit(1)

# These are commands for blocking/unblocking a website
# Usage: python3 proxy.py --block=google.com or python3 proxy.py -b google.com
@click.command()
@click.option('--block', '-b', help='Add a site to the list of blocked sites')
@click.option('--unblock', '-u', help='Remove a site from the list of blocked sites')
def main(block, unblock):
    # If the website is already blocked, don't do anything. If not, block it
    if block:
        if website_blocked(block):
            print(block + " is already blocked")
        else:
            with open('blocklist.txt', 'a') as blocklist:
                blocklist.write(block)
            print(block + " added to blocklist")

    # If the website is already unblocked, don't do anything. If not, block it
    elif unblock:
        if not website_blocked(unblock):
            print(unblock + " is already unblocked")
        else:
            f = open('blocklist.txt', 'r')
            lines = f.readlines()
            f.close()

            with open('blocklist.txt', 'w') as out:
                for line in lines:
                    line_str = line.strip('\n')
                    if line_str != unblock:
                        out.write(line)
            print(unblock + " removed from blocklist")

    # Starting the proxy server as normal
    else:
        print("Starting proxy server...")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', 8080))
            s.listen(20)
            print("Listening on port 8080")
            print("======================\n")
        except Exception:
            if s:
                s.close()
            print(message)
            sys.exit(1)

        # Listen for incoming requests and dispatch a new Thread to handle each one
        while 1:
            (clientsocket, address) = s.accept()
            threading.Thread(target=proxy_thread, args=(clientsocket, address)).start()
        s.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping server...")
        sys.exit(1)
