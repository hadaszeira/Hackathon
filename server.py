import selectors
import socket
import struct
import threading as threads
import time
import types
import formats

my_client_list = []
group1 = []
group2 = []
score_group1 = 0
score_group2 = 0


def update_scores(data_outb):
    global score_group1
    global score_group2

    data = repr(data_outb)
    team = data[2: len(data) - 3]
    if team in group1:
        score_group1 += 1
    if team in group2:
        score_group2 += 1
    else:
        print("team:" + team)
        print("Error: update scores")


def check_team_name(data_out):
    data = repr(data_out)
    if len(data) > 1:  # and data[len(data) - 2] == '\n':
        return data
    return ""


def accept_wrapper(sel, sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
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
            # data.outb += recv_data
            team_name = check_team_name(recv_data)
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    # if mask & selectors.EVENT_WRITE:
    #     if data.outb:
    #         print('echoing', repr(data.outb), 'to', data.addr)
    #         sent = sock.send(data.outb)  # Should be ready to write
    #         data.outb = data.outb[sent:]
    return team_name


def send_msg_to_clients(sel, key, mask, msg):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_WRITE:
        try:
            sent = sock.send(msg)  # Should be ready to write
            data.outb = data.outb[sent:]
        except:
            print("Error welcome")
            pass
    # if mask & selectors.EVENT_READ:
    #     recv_data = sock.recv(1024)  # Should be ready to read
    #     if recv_data:
    #          data.outb += recv_data
    #     else:
    #         print('closing connection to', data.addr)
    #         sel.unregister(sock)
    #         sock.close()
    # if mask & selectors.EVENT_WRITE:
    #      # if data.outb:
    #          # print('echoing', repr(data.outb), 'to', data.addr)
    #  try:
    #     sent = sock.send(msg)  # Should be ready to write
    #     data.outb = data.outb[sent:]
    #  except:
    #     print("Error welcome")
    #     pass


def service_game_begins(sel, key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            # data.outb = recv_data
            update_scores(recv_data)
            # data.outb = data.outb[0:]
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    # if mask & selectors.EVENT_WRITE:
    #     sent = sock.send(welcome_msg)
    #     data.outb = data.outb[sent:]


def unregi_client(sel, key, mask):
    sock = key.fileobj
    data = key.data

    print('closing connection to', data.addr)
    sel.unregister(sock)
    sock.close()
    # if mask & selectors.EVENT_READ:
    #     recv_data = sock.recv(1024)  # Should be ready to read
    #     if recv_data:
    #         data.outb = recv_data
    #     else:
    #         print('closing connection to', data.addr)
    #         sel.unregister(sock)
    #         sock.close()
    # if mask & selectors.EVENT_WRITE:
    #     sent = sock.send(bye_msg)
    #     data.outb = data.outb[sent:]


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
            # print("times up!!!  -->  server broadcasting stopped.")
            break
        server.sendto(message, (ips[ip_index], 13117))
        # print("message sent to %s" % ips[ip_index])
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

    print("Game over, sending out offer requests...")


def main():
    global score_group1
    global score_group2
    global my_client_list

    main_loop = True
    while main_loop:
        broadcast_thread = threads.Thread(name="t1", target=send_udp_broadcast)
        broadcast_thread.setDaemon(True)  # runs in the background without worrying about shutting it down.
        broadcast_thread.start()

        sel = selectors.DefaultSelector()
        HOST = '10.0.2.15'  # Standard loop back interface address (localhost)
        PORT = 13117  # Port to listen on (non-privileged ports are > 1023)
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((HOST, PORT))
        lsock.listen()
        print('Server started, listening on IP address ', (HOST, PORT))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)

        timeout = time.time() + 10  # 10 seconds from now

        while time.time() < timeout:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(sel, key.fileobj)
                    my_client_list.append((key, mask))
                else:
                    team_name = service_connection(sel, key, mask)
                    if len(team_name) > 1 and team_name not in group1 and team_name not in group2:
                        if len(group1) >= len(group2):
                            group2.append(team_name[2: len(team_name)-3])
                        else:
                            group1.append(team_name[2: len(team_name)-3])

        broadcast_thread.join()
        # print("Welcome to Keyboard Spamming Battle Royal.")
        # print("Group 1: \n==\n" + str(group1))
        # print("Group 2: \n==\n" + str(group2))
        # print("Start pressing keys on your keyboard as fast as you can!!")
        welcome_msg = "Welcome to Keyboard Spamming Battle Royal.\nGroup 1: \n==\n"
        for t in group1:
            welcome_msg += t + '\n'
        welcome_msg += "Group 2: \n==\n"
        for t in group2:
            welcome_msg += t + '\n'
        welcome_msg += "Start pressing keys on your keyboard as fast as you can!!\n"
        print(welcome_msg)
        welcome_msg = bytes(welcome_msg, 'utf-8')

        # welcome_msg = b'Welcome msg ~~'

        events = sel.select(timeout=None)
        for key, mask in events:
            send_msg_to_clients(sel, key, mask, welcome_msg)

        timeout2 = time.time() + 10
        while time.time() < timeout2:
            events = sel.select(timeout=None)
            for key, mask in events:
                service_game_begins(sel, key, mask)

        events = sel.select(timeout=None)
        for key, mask in events:
            send_msg_to_clients(sel, key, mask, b"byebye")

        print("Game over!\nGroup 1 typed in %d characters. Group 2 typed %d characters." % (score_group1, score_group2))
        if score_group1 > score_group2:
            print("Group 1 Wins!")
        if score_group1 < score_group2:
            print("Group 2 Wins!")
        else:
            print("Unbelievable! It's a tie!")

        events = sel.select(timeout=None)
        for key, mask in events:
            unregi_client(sel, key, mask)
        finish_main_loop()
        lsock.close()

        time.sleep(2)
        print("\n\n---------------\n\n")


if __name__ == "__main__":
    main()

