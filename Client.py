import os
from socket import *

# HOST = '127.0.0.1'
PORT = 8910
BUF_SIZE = 64
status = True


while status:

    connection = False
    command = input("Enter a command: ")
    com_split = command.split()
    com1 = com_split[0]

    if com1 == 'connect' and len(com_split) == 3:
        send = 'CONNECT {}'.format(com_split[2])
        HOST = com_split[2]
        print(HOST)
        #connecting to server
        # with socket(AF_INET, SOCK_STREAM) as s:
        s = socket(AF_INET, SOCK_STREAM)
        try:
            s.connect((HOST, PORT))
            s.send(f'CONNECT {com_split[1]}'.encode())
            ans = s.recv(BUF_SIZE).decode()
            if ans.split()[0] == 'Welcome':
                connection = True
            print(ans)
        except Exception as e:
            print('IP address is not valid or server is not responding')
            print(e)
            continue
    elif com1 == 'quit':
        status = False

    else:
        print("Error: You are not connected to server")

    while connection:

        command = input("Enter a command: ")
        com_split = command.split()
        com1 = com_split[0]


        if com1 == 'disconnect':
            s.send('DISCONNECT'.encode())
            print('Disconnected')
            connection = False
            s.close()

        elif com1 == 'quit':
            s.send('QUIT'.encode())
            status = False
            connection = False

        elif com1 == 'lu':
            # print('LU')
            s.send('LU'.encode())
            print(s.recv(BUF_SIZE).decode())

        elif com1 == 'send':
            if com_split[1] == 'not_online':
                print('Error: User is not online')
                continue
            msg = command[command.find('“') + 1:command.find('”')]
            send = 'MESSAGE {}\n{} {}'.format(com_split[1], len(msg), msg)
            print(send)

        elif com1 == 'lf':
            s.send('LF'.encode())
            print(s.recv(BUF_SIZE).decode())

        #maybe create functions to read and write for using them in over- and appendfiles commands
        elif com1 == 'read':
            if com_split[1] == 'already_exists':
                print('Error: Client already contains that file')
                continue
            send = 'READ {}'.format(com_split[1])
            print(send)
            # wait for response

        elif com1 == 'write':
            if com_split[1] == 'already_exists':
                print('Error: Server already contains that file')
                continue
            send1 = 'WRITE {}'.format(com_split[1])
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

print('Connections are terminated and program is closed')