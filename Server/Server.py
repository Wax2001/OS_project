from socket import *
from os import path, listdir
from threading import Thread

HOST = '127.0.0.1'
# HOST = '192.168.31.15'
PORT = 2021
RECV_PORT = 2022
BUF_SIZE = 1024
users_dict = {}
file_using = []
users_using = []
messages = {}

def thread_for_client(conn, username):
    global users_dict, file_using, messages
    recv_mode = ['WRITE', 'OVERWRITE', 'APPEND', 'APPENDFILE']
    connection = True
    recv_sock = socket(AF_INET, SOCK_STREAM)
    recv_sock.connect((users_dict[username], RECV_PORT))

    while connection:
        for i in messages[username]:
            print(i)
            recv_sock.send(i.encode('ascii'))
        messages[username].clear()
        conn.settimeout(0.1)
        try:
            command = conn.recv(BUF_SIZE).decode('ascii')
        except timeout:
            continue
        if command:
            com0 = command.split()[0]
            if len(command.split()) > 1:
                com1 = command.split()[1]

            if com0 == 'LU':
                lu = ''
                for name in users_dict:
                    lu += '{} '.format(name)
                lu += '\n'
                print('Sending LU for {}'.format(username))
                conn.send(lu.encode('ascii'))

            elif com0 == 'LF':
                lf = ''
                for file in listdir('server_files'):
                    lf += '{} '.format(file)
                lf += '\n'
                print('Sending LF for {}'.format(username))
                conn.send(lf.encode('ascii'))

            elif com0 == 'DISCONNECT':
                try:
                    recv_sock.send("DISCONNECT\n".encode('ascii'))
                    recv_sock.close()
                    users_dict.pop(username)
                    messages.pop(username)
                    conn.send('OK\n'.encode('ascii'))
                    conn.close()
                    print('{} is disconnected'.format(username))
                    break
                except Exception as e:
                    print('Couldnt disconnect {}. {}'.format(username, e))
                    conn.send('ERROR\n'.encode('ascii'))

            elif com0 == 'MESSAGE':
                if com1 in users_dict.keys():
                    # users_using.append(com1)
                    # try:
                    #     recv_sock.connect((users_dict[com1], RECV_PORT))
                    # except Exception as e:
                    #     print('Couldnt deliver {}s message: {}'.format(username, e))
                    #     conn.send('ERROR\n'.encode())
                    #     continue
                    msg = command.replace(' ' + com1, '')
                    messages[com1].append(msg)
                    # recv_sock.send(msg.encode())
                    # users_using.remove(com1)
                    print('{} sent {} a message'.format(username, com1))
                    # recv_sock.close()
                else:
                    conn.send("ERROR\n".encode('ascii'))

            elif com0 == 'READ':
                filepath = 'server_files/' + com1
                if path.exists(filepath):
                    if filepath not in file_using:
                        file_using.append(filepath)
                    else:
                        conn.send("ERROR\n".encode('ascii'))
                        continue

                    print('Sending {} to {}'.format(com1, username))
                    conn.send("OK\n".encode('ascii'))
                    file = open(filepath, 'r')
                    size = str(path.getsize(filepath))
                    part = size + ' ' + file.read(BUF_SIZE - len(size) - 1)
                    while part:
                        conn.send(part.encode())
                        # print('Sent ', repr(part))
                        part = file.read(BUF_SIZE)
                    file.close()
                    file_using.remove(filepath)
                    print('Everything sent')
                else:
                    conn.send("ERROR\n".encode('ascii'))

            elif com0 in recv_mode:
                filepath = 'server_files/' + command.split()[-1]
                if (path.exists(filepath) and com0 == 'WRITE'):
                    conn.send('ERROR\n'.encode('ascii'))
                elif (not path.exists(filepath) and com0[:6] == 'APPEND'):
                    conn.send('ERROR\n'.encode('ascii'))
                else:
                    if filepath not in file_using:
                        file_using.append(filepath)
                    else:
                        conn.send("ERROR\n".encode('ascii'))
                        continue
                    conn.send('OK\n'.encode('ascii'))
                    meth = 'w'
                    if com0[:6] == 'APPEND':
                        meth = 'a'
                    print(meth)
                    with open(filepath, meth) as file:
                        print('Receiving file from ', username)
                        data = conn.recv(BUF_SIZE).decode()
                        size = int(data.split()[0])
                        data = data[data.find(' ')+1:]
                        file.write(data)
                        size -= len(data)
                        while size > 0:
                            data = conn.recv(BUF_SIZE).decode()
                            # print('data = {}\n'.format(data))
                            # write data to a file
                            file.write(data)
                            size -= BUF_SIZE
                    print('File received with size of ', path.getsize(filepath))
                    file.close()
                    file_using.remove(filepath)


            else:
                conn.send("ERROR\n".encode('ascii'))
        else:
            connection = False

try:
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        print('Waiting for new connection')
        client_socket, client_address = s.accept()
        # print(clientsocket)
        name_check = client_socket.recv(BUF_SIZE).decode('ascii')
        username = name_check.split()[1]
        if username in users_dict:
            client_socket.send('ERROR\n'.encode('ascii'))
            continue
        else:
            users_dict[username] = client_address[0]
            messages[username]=[]
            client_socket.send('OK\n'.encode('ascii'))
            print('User {} connected to the server'.format(username))
        client_thread = Thread(target=thread_for_client, args=(client_socket, username), daemon=True)
        client_thread.start()
except KeyboardInterrupt:
    # recv_sock = socket(AF_INET, SOCK_STREAM)
    for us in users_dict:
        msg = "DISCONNECT\n"
        messages[us].append(msg)
        # recv_sock.connect((users_dict[us], RECV_PORT))
        # recv_sock.send("DISCONNECT\n".encode())
    if not messages.values():
        print('Server closed')
        # recv_sock.close()
        s.close()
