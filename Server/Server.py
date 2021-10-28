from socket import *
from os import path, listdir
from threading import Thread

HOST = '127.0.0.1'
# HOST = '192.168.31.15'
PORT = 2021
RECV_PORT = 2022
BUF_SIZE = 1024
users_dict = {}


def thread_for_client(conn, username):
    global users_dict
    recv_mode = ['WRITE', 'OVERWRITE', 'APPEND', 'APPENDFILE']
    connection = True
    recv_sock = socket(AF_INET, SOCK_STREAM)
    while connection:
        command = conn.recv(BUF_SIZE).decode()
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
                conn.send(lu.encode())

            elif com0 == 'LF':
                lf = ''
                for file in listdir('server_files'):
                    lf += '{} '.format(file)
                lf += '\n'
                print('Sending LF for {}'.format(username))
                conn.send(lf.encode())

            elif com0 == 'DISCONNECT':
                try:
                    recv_sock.connect((users_dict[username], RECV_PORT))
                    recv_sock.send("DISCONNECT".encode())
                    recv_sock.close()
                    users_dict.pop(username)
                    conn.send('OK'.encode())
                    conn.close()
                    print('{} is disconnected'.format(username))
                    break
                except Exception as e:
                    print('Couldnt disconnect {}. {}'.format(username, e))
                    conn.send('ERROR'.encode())

            elif com0 == 'MESSAGE':
                if com1 in users_dict.keys():
                    try:
                        recv_sock.connect((users_dict[com1], RECV_PORT))
                    except Exception as e:
                        print('Couldnt deliver message: ', e)
                        conn.send('Connection to receiving thread failed'.encode())
                        continue
                    msg = command.replace(com1, '')
                    recv_sock.send(msg.encode())
                    print('{} sent {} a message'.format(username, com1))
                else:
                    conn.send("{} is not online".format(command.split()[1]).encode())

            elif com0 == 'READ':
                filepath = 'server_files/' + com1
                if path.exists(filepath):
                    print('Sending {} to {}'.format(com1, username))
                    conn.send("OK".encode())
                    file = open(filepath, 'r')
                    size = str(path.getsize(filepath))
                    part = size + ' ' + file.read(BUF_SIZE - len(size) - 1)
                    while part:
                        conn.send(part.encode())
                        # print('Sent ', repr(part))
                        part = file.read(BUF_SIZE)
                    file.close()
                    print('Everything sent')
                else:
                    conn.send("ERROR".encode())

            elif com0 in recv_mode:
                filepath = 'server_files/' + command.split()[-1]
                if (path.exists(filepath) and com0 == 'WRITE') or (not path.exists(filepath) and com0[:6] == 'APPEND'):
                    conn.send('ERROR'.encode())
                else:
                    conn.send('OK'.encode())
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


            else:
                conn.send("Comm not added".encode())
        else:
            connection = False


s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
while True:
    print('Waiting for new connection')
    client_socket, client_address = s.accept()
    # print(clientsocket)
    name_check = client_socket.recv(BUF_SIZE).decode()
    username = name_check.split()[1]
    if username in users_dict:
        client_socket.send('ERROR'.encode())
        continue
    else:
        users_dict[username] = client_address[0]
        client_socket.send('OK'.encode())
        print('User {} connected to the server'.format(username))
    client_thread = Thread(target=thread_for_client, args=(client_socket, username), daemon=True)
    client_thread.start()

s.close()
