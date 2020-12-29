import selectors
import socket
import struct
import threading as threads
import time
import types
import formats

group1 = []
group2 = []
group1_addrs = []
group2_addrs = []
score_group1 = 0
score_group2 = 0


def update_scores(data_outb, data_addr):
    global score_group1
    global score_group2

    data = data_outb.decode("utf-8")
    print(data)
    # team = data[2: len(data) - 3]
    # if team in group1:
    #     score_group1 += 1
    # if team in group2:
    #     score_group2 += 1
    if data_addr in group1_addrs:
        score_group1 += 1
    elif data_addr in group2_addrs:
        score_group2 += 1
    else:
        print("Error: update scores! ---> addr:" + data_addr)


def check_team_name(data_out):
    data = repr(data_out)
    if len(data) > 1:
        return data
    return ""


def accept_wrapper(sel, sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(formats.PrintColors.OKGREEN + 'accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(sel, key, mask):
    team_name = ""
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            team_name = check_team_name(recv_data)
        else:
            print('closing connection to', data.addr)
            try:
                sel.unregister(sock)
                sock.close()
            except:
                print("Error: service_connection func")
                pass
    return team_name, data.addr


def send_msg_to_clients(sel, key, mask, msg):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_WRITE:
        try:
            sent = sock.send(msg)  # Should be ready to write
            data.outb = data.outb[sent:]
        except:
            print("Error: send_msg_to_clients")
            pass


def service_game_begins(sel, key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            update_scores(recv_data, data.addr)
        else:
            print('closing connection to', data.addr)
            try:
                sel.unregister(sock)
                sock.close()
            except:
                print("Error: service_game_begins func")
                pass


def unregi_client(sel, key, mask):
    sock = key.fileobj
    data = key.data

    print(formats.PrintColors.purple + 'closing connection to', data.addr)
    try:
        sel.unregister(sock)
        sock.close()
    except:
        print("Error: unregi_client func")
        pass


def create_ips_list(ip_format):
    ips = []
    i = 0
    while i < 256:
        ip = ip_format + str(i)
        ips.append(ip)
        i += 1
    return ips


def send_udp_broadcast():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Enable broadcasting mode
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    port_in_format = struct.pack('>H', 13117)  # port in 2 bytes
    message = formats.BrodMSG(port_in_format).msg_to_bytes()
    ip_format = "10.0.2."
    ips = create_ips_list(ip_format)

    timeout = time.time() + 10  # 10 seconds from now
    ip_index = 0

    while True:
        if time.time() > timeout:
            break
        server.sendto(message, (ips[ip_index], 13117))
        if ip_index < (len(ips)-1):
            ip_index += 1
        else:
            ip_index = 0
    server.close()


def finish_main_loop():
    global score_group1
    global score_group2
    global group1
    global group2

    score_group1 = 0
    score_group2 = 0
    group1 = []
    group2 = []


def create_welcome_msg():
    welcome_msg = "\nWelcome to Keyboard Spamming Battle Royal.\nGroup 1: \n==\n"
    for t in group1:
        welcome_msg += t + '\n'
    welcome_msg += "Group 2: \n==\n"
    for t in group2:
        welcome_msg += t + '\n'
    welcome_msg += "Start pressing keys on your keyboard as fast as you can!!\n"
    print(formats.PrintColors.OKCYAN + welcome_msg)
    welcome_msg = bytes(welcome_msg, 'utf-8')
    return welcome_msg


def main():
    global score_group1
    global score_group2

    # Stage 1: open TCP socket and listening
    sel = selectors.DefaultSelector()
    HOST = '10.0.2.15'  # Standard loop back interface address (localhost)
    PORT = 13117  # Port to listen on (non-privileged ports are > 1023)
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print(formats.PrintColors.OKGREEN + 'Server started, listening on IP address ', (HOST, PORT))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    main_loop = True
    while main_loop:
        # Stage 1: UDP broadcast msgs to all clients
        broadcast_thread = threads.Thread(name="t1", target=send_udp_broadcast)
        broadcast_thread.setDaemon(True)  # runs in the background without worrying about shutting it down.
        broadcast_thread.start()

        # Stage 2: open TCP connections with clients and divide to groups
        timeout = time.time() + 10  # 10 seconds from now
        while time.time() < timeout:
            events = sel.select(timeout=timeout-time.time())
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(sel, key.fileobj)
                else:
                    team_name, team_addr = service_connection(sel, key, mask)
                    if len(team_name) > 1 and team_name not in group1 and team_name not in group2:
                        if len(group1) >= len(group2):
                            group2.append(team_name[2: len(team_name)-3])
                            group2_addrs.append(team_addr)
                        else:
                            group1.append(team_name[2: len(team_name)-3])
                            group1_addrs.append(team_addr)

        broadcast_thread.join()

        # Stage 3: send Welcome msgs to all clients
        welcome_msg = create_welcome_msg()
        events = sel.select(timeout=None)
        for key, mask in events:
            send_msg_to_clients(sel, key, mask, welcome_msg)

        # Stage 4: listening to all clients who type on keyboard and counts
        timeout2 = time.time() + 10
        while time.time() < timeout2:
            events = sel.select(timeout=None)
            for key, mask in events:
                service_game_begins(sel, key, mask)

        # Stage 5: send Game-Over msgs to all clients
        events = sel.select(timeout=None)
        for key, mask in events:
            send_msg_to_clients(sel, key, mask, b"GAME-OVER!\n")

        # Stage 6: print game summary
        print(formats.PrintColors.OKBLUE +
              "Game over!\nGroup 1 typed in %d characters. Group 2 typed %d characters." % (score_group1, score_group2))
        if score_group1 > score_group2:
            print(formats.PrintColors.OKBLUE + formats.PrintColors.BOLD + "Group 1 Wins!")
            print(formats.PrintColors.OKBLUE + "Congratulations to the winners:\n==")
            for t in group1:
                print(formats.PrintColors.OKBLUE + t + "\n")
        if score_group1 < score_group2:
            print(formats.PrintColors.OKBLUE + formats.PrintColors.BOLD + "Group 2 Wins!")
            print(formats.PrintColors.OKBLUE + "Congratulations to the winners:\n==")
            for t in group2:
                print(formats.PrintColors.OKBLUE + t + "\n")
        else:
            print(formats.PrintColors.OKBLUE + "Unbelievable! It's a tie!")

        # Stage 7: unregister all clients
        events = sel.select(timeout=None)
        for key, mask in events:
            unregi_client(sel, key, mask)

        # Stage 8: close socket and loop again
        print(formats.PrintColors.purple + "Game over, sending out offer requests...")
        finish_main_loop()
        # lsock.close()

        # time.sleep(2)
        print(formats.PrintColors.purple + "\n=================\n")


if __name__ == "__main__":
    main()

