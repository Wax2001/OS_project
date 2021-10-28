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
    connection = True
    send_mode = ['write', 'overwrite', 'appendfile']
    while connection:
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
                connection = False
            else:
                print('Disconnection error')

        elif com1 == 'quit':
            socket.send('DISCONNECT'.encode())
            if socket.recv(BUF_SIZE).decode() == 'OK':
                print('Quitting')
                socket.close()
                status = False
                connection = False
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

        # maybe create functions to read and write for using them in over- and append server_files commands
        elif com1[-4:] == 'read':
            if com_split[1] not in os.listdir('client_files/') or com1 == "overread":
                socket.send('READ {}'.format(com_split[1]).encode())
                if socket.recv(BUF_SIZE).decode() == 'OK':
                    with open('client_files/' + com_split[1], 'w') as file:
                        print('Receiving file')
                        data = socket.recv(BUF_SIZE).decode()
                        size = int(data.split()[0])
                        data = data[data.find(' ') + 1:]
                        file.write(data)
                        size -= len(data)
                        while size > 0:
                            data = socket.recv(BUF_SIZE).decode()
                            # print('data = {}\n'.format(data))
                            # write data to a file
                            file.write(data)
                            size -= BUF_SIZE
                    print('File received with size of ', os.path.getsize('client_files/' + com_split[1]))
                    file.close()
            else:
                print('ERROR: You already have that file.')

        elif com1 in send_mode:
            filepath = 'client_files/' + com_split[1]
            if com_split[1] not in os.listdir('client_files/'):
                print('ERROR: You dont have such file.')
                continue
            if com1 == 'appendfile':
                socket.send('{} {} {}'.format(com1.upper(), com_split[1], com_split[2]).encode())
            else:
                socket.send('{} {}'.format(com1.upper(), com_split[1]).encode())
            if socket.recv(BUF_SIZE).decode() == 'OK':
                print('Sending {} to server'.format(com1))
                file = open(filepath, 'r')
                size = str(os.path.getsize(filepath))
                part = size + ' ' + file.read(BUF_SIZE - len(size) - 1)
                while part:
                    socket.send(part.encode())
                    # print('Sent ', repr(part))
                    part = file.read(BUF_SIZE)
                file.close()
                print('Everything sent')
            else:
                print('ERROR: This file already exists on server.')

        elif com1 == 'append':
            socket.send('{} {}'.format(com1.upper(), com_split[-1]).encode())
            if socket.recv(BUF_SIZE).decode() == 'OK':
                content = command[command.find('“') + 1:command.find('”')]
                socket.send((str(len(content)) + ' ' + content).encode())
                print('Everything sent')
            else:
                print('ERROR: This file already exists on server.')

        else:
            print("Error: Command is wrong or non_existent")
        screen_lock.release()
        time.sleep(1)


def receiving_thread():
    rs = socket(AF_INET, SOCK_STREAM)
    rs.bind((HOST, RECV_PORT))
    rs.listen()

    while True:
        serv_sock, serv_addr = rs.accept()
        message = serv_sock.recv(BUF_SIZE).decode()
        if message == "DISCONNECT":
            rs.close()
            break

        elif message:
            screen_lock.acquire()
            print(message)
            screen_lock.release()
            time.sleep(1)

        else:
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

        st = Thread(target=sending_thread, args=(s,))
        # Thread(target=receiving_thread, daemon=True).start()
        rt = Thread(target=receiving_thread)

        st.start()
        rt.start()

        st.join()
        rt.join()

        s.close()

    elif com_split[0] == 'quit':
        status = False

    else:
        print("Error: You are not connected to server")

print('Connections are terminated and program is closed')
