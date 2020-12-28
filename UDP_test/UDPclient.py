import socket

client = socket.socket(socket.AF_INET,  # Internet
                       socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP

client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

client.bind(("", 37020))
while True:
    data, addr = client.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message: %s" % data)
    print("from address: %s, %s" % (addr[0],  addr[1]))
