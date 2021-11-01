import os
import time
from socket import *
from threading import Thread, Lock

HOST = '127.0.0.1'
# HOST = '192.168.238.241'
SEND_PORT = 2021
RECV_PORT = 2022
BUF_SIZE = 1024
status = True
connection = True
con_rec = True
screen_lock = Lock()


def sending_thread(socket):
    global status, connection
    write_mode = ['write', 'overwrite', 'appendfile']
    while connection:
        screen_lock.acquire()
        command = input("Enter a command: ")
        if not connection:
            screen_lock.release()
            break
        com_split = command.split()
        com1 = com_split[0]

        if com1 == 'disconnect':
            socket.send('DISCONNECT\n'.encode('ascii'))
            if socket.recv(BUF_SIZE).decode('ascii')[:2] == 'OK':
                print('Disconnecting')
                socket.close()
                # connection = False
            else:
                print('Disconnection error')

        elif com1 == 'quit':
            socket.send('DISCONNECT\n'.encode('ascii'))
            if socket.recv(BUF_SIZE).decode('ascii')[:2] == 'OK':
                print('Quitting')
                socket.close()
                status = False
                # connection = False
            else:
                print('Quit error')

        elif com1 == 'lu':
            # print('LU')
            socket.send('LU\n'.encode('ascii'))
            print(socket.recv(BUF_SIZE).decode('ascii'))

        elif com1 == 'send' and len(com_split) > 2:
            msg = command[command.find('“') + 1:command.find('”')]
            send_msg = 'MESSAGE {}\n{} {}\n'.format(com_split[1], str(len(msg)), msg)
            socket.send(send_msg.encode('ascii'))
            socket.settimeout(2)
            # try:
            r = socket.recv(BUF_SIZE).decode('ascii')
            print(r)
            if r == 'OK\n':
                print('Message has been sent')

            # except timeout:
            #     print('Message has been sent')

        elif com1 == 'lf':
            socket.send('LF\n'.encode('ascii'))
            print(socket.recv(BUF_SIZE).decode('ascii'))

        elif com1[-4:] == 'read':
            if com_split[1] not in os.listdir('client_files/') or com1 == "overread":
                socket.send('READ {}\n'.format(com_split[1]).encode('ascii'))
                r = socket.recv(BUF_SIZE).decode('ascii')
                if r[:2] == 'OK':
                    size = ''
                    c = socket.recv(1).decode('ascii')
                    while ' ' != c:
                        size += c
                        c = socket.recv(1).decode('ascii')
                    size = int(size)
                    to_read = socket.recv(size)
                    with open('client_files/' + com_split[1], 'wb') as file:
                        file.write(to_read)
                    print('File received with size of ', os.path.getsize('client_files/' + com_split[1]))
                else:
                    print(r)
            else:
                print('ERROR\n')

        elif com1 in write_mode:
            filepath = 'client_files/' + com_split[1]
            if com_split[1] not in os.listdir('client_files/'):
                print('ERROR\n')
                continue
            if com1 == 'appendfile':
                socket.send('{} {} {}\n'.format(com1.upper(), com_split[1], com_split[2]).encode('ascii'))
            else:
                socket.send('{} {}\n'.format(com1.upper(), com_split[1]).encode('ascii'))
            r = socket.recv(BUF_SIZE).decode('ascii')
            if r[:2] == 'OK':
                print('Sending {} to server'.format(com1))
                size = str(os.path.getsize(filepath))
                socket.send('{} '.format(size).encode('ascii'))
                with open(filepath, 'rb') as file:
                    data = file.read()
                    socket.sendall(data)
                print('Everything sent')
                print(socket.recv(BUF_SIZE).decode('ascii'))
            else:
                print(r)

        elif com1 == 'append':
            socket.send('{} {}\n'.format(com1.upper(), com_split[-1]).encode('ascii'))
            r = socket.recv(BUF_SIZE).decode('ascii')
            if r[:2] == 'OK':
                content = command[command.find('“') + 1:command.find('”')]
                socket.send((str(len(content)) + ' ' + content).encode('ascii'))
                print('Everything sent')
                print(socket.recv(BUF_SIZE).decode('ascii'))
            else:
                print(r)

        else:
            print("Error\n")
        screen_lock.release()
        time.sleep(1)


def receiving_thread():
    global connection
    rs = socket(AF_INET, SOCK_STREAM)
    rs.bind((HOST, RECV_PORT))
    rs.listen()
    serv_sock, serv_addr = rs.accept()

    while con_rec:
        serv_sock.settimeout(0.1)
        try:
            message = serv_sock.recv(BUF_SIZE).decode('ascii')

            if message == "DISCONNECT\n":
                connection = False
                screen_lock.acquire()
                print('You were disconnected')
                screen_lock.release()
                rs.close()
                break

            elif message:
                size = int(message.split()[1])
                full_msg = message[message.find(' ', 8) + 1:]
                size -= len(message)
                while size > 0:
                    message = serv_sock.recv(BUF_SIZE).decode('ascii')
                    full_msg += message
                    size -= BUF_SIZE
                screen_lock.acquire()
                print('MESSAGE\n', full_msg)
                screen_lock.release()
                time.sleep(0.1)

            else:
                break
        except timeout:
            continue
        except:
            break
    rs.close()


while status:
    command = input("Enter a command: ")
    com_split = command.split()

    if com_split[0] == 'connect' and len(com_split) == 3:
        ip = com_split[2]
        s = socket(AF_INET, SOCK_STREAM)
        rt = Thread(target=receiving_thread)
        rt.start()
        try:
            s.connect((ip, SEND_PORT))
            s.send(f'CONNECT {com_split[1]}\n'.encode('ascii'))
            ans = s.recv(BUF_SIZE).decode('ascii')
            if ans[:6] == 'ERROR':
                con_rec = False
                print('Server denied connection. Try again')
                continue
            elif ans[:2] == 'OK':
                print("Successful connection")
        except Exception as e:
            con_rec = False
            print('IP address is not valid or server is not responding')
            print(e)
            continue

        connection = True
        st = Thread(target=sending_thread, args=(s,))
        # Thread(target=receiving_thread, daemon=True).start()

        st.start()

        st.join()
        rt.join()

        s.close()

    elif com_split[0] == 'quit':
        connection = False
        con_rec = False
        status = False

    else:
        print("Error: You are not connected to server")

print('Connections are terminated and program is closed')
