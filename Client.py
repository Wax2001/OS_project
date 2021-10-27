import os
import time
from socket import *
from threading import Thread, Lock

HOST = '127.0.0.1'
SEND_PORT = 2021
RECV_PORT = 2022
BUF_SIZE = 1024
status = True
screen_lock = Lock()


def sending_thread(socket):
    while True:
        global status
        screen_lock.acquire()
        command = input("Enter a command: ")
        com_split = command.split()
        com1 = com_split[0]

        if com1 == 'disconnect':
            socket.send('DISCONNECT'.encode())
            if socket.recv(BUF_SIZE).decode() == 'OK':
                print('Disconnecting')
                socket.close()
                break
            else:
                print('Disconnection error')

        elif com1 == 'quit':
            socket.send('DISCONNECT'.encode())
            if socket.recv(BUF_SIZE).decode() == 'OK':
                print('Quitting')
                socket.close()
                status = False
                break
            else:
                print('Quit error')

        elif com1 == 'lu':
            # print('LU')
            socket.send('LU'.encode())
            print(socket.recv(BUF_SIZE).decode())

        elif com1 == 'send' and len(com_split) > 2:

            msg = command[command.find('“') + 1:command.find('”')]
            send_msg = 'MESSAGE {}\n{} {}'.format(com_split[1], len(msg), msg)
            socket.send(send_msg.encode())
            socket.settimeout(2)
            try:
                print(socket.recv(BUF_SIZE).decode())
            except timeout:
                print('Message has been sent')

        elif com1 == 'lf':
            socket.send('LF'.encode())
            print(socket.recv(BUF_SIZE).decode())

        # maybe create functions to read and write for using them in over- and append files commands
        elif com1 == 'read':
            if com_split[1] == 'already_exists':
                print('Error: Client already contains that file')
                continue
            send = 'READ {}'.format(com_split[1])
            print(send)

        elif com1 == 'write':
            if com_split[1] == 'already_exists':
                print('Error: Server already contains that file')
                continue
            send = 'WRITE {}'.format(com_split[1])
            print(send)
            # wait for response
            # file_size = os.path.getsize('path')
            # send2 = '{} {}'.format(file_size, file_cont)
            print('23456 filecontent')

        elif com1 == 'append':
            if com_split[-1] == 'not_here':
                print('Error: Server does not contain that file')
                continue
            send = 'APPEND {}'.format(com_split[-1])
            print(send)
            # wait for response
            add_data = command[command.find('“') + 1:command.find('”')]
            # file_size = os.path.getsize('path')
            print('{} {}'.format(len(add_data), add_data))

        else:
            print("Error: Command is wrong or non_existent")
        screen_lock.release()
        time.sleep(1)


def receiving_thread():
    with socket(AF_INET, SOCK_STREAM) as rs:
        rs.bind((HOST, RECV_PORT))
        rs.listen()

        while True:
            serv_sock, serv_addr = rs.accept()
            message = serv_sock.recv(BUF_SIZE).decode()
            if message:
                screen_lock.acquire()
                print(message)
                screen_lock.release()
                time.sleep(1)
            else:
                screen_lock.release()
                break


while status:
    command = input("Enter a command: ")
    com_split = command.split()

    if com_split[0] == 'connect' and len(com_split) == 3:
        ip = com_split[2]
        s = socket(AF_INET, SOCK_STREAM)
        try:
            s.connect((ip, SEND_PORT))
            s.send(f'CONNECT {com_split[1]}'.encode())
            ans = s.recv(BUF_SIZE).decode()
            if ans == 'ERROR':
                print('Server denied connection. Try again')
                continue
            elif ans == 'OK':
                print("Successful connection")
        except Exception as e:
            print('IP address is not valid or server is not responding')
            print(e)
            continue

        Thread(target=receiving_thread, daemon=True).start()
        st = Thread(target=sending_thread, args=(s,))
        # rt = Thread(target=receiving_thread)
        st.start()
        # rt.start()
        st.join()
        # rt.join()
        s.close()

    elif com_split[0] == 'quit':
        status = False

    else:
        print("Error: You are not connected to server")

print('Connections are terminated and program is closed')
