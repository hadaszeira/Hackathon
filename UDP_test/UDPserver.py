import socket
import time

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
server.settimeout(0.2)
message = b"your very important message"
my_ip = '10.0.2.15'
# todo go over all the range of the last number in th ip
# while 10 sconds
while True:
    # '<broadcast>'
    server.sendto(message, (my_ip, 37020))
    print("message sent!")
    time.sleep(1)

