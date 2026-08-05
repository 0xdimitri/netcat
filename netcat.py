#comments are added for my understanding and learning purposes.
import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    try:
        output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
        return output.decode()
    except Exception as e:
        return f"Command execution failed: {str(e)}\n"

class NetCat:

    def __init__(self, args, buffer=None):
        self.args= args #store the parsed arguments in the instance variable
        self.buffer = buffer #store the buffer in the instance variable
        self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a TCP socket using IPv4 addressing
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #set the socket option to allow reuse of local addresses

    def run(self):
        if self.args.listen:
            self.listen() #if listen flag is set, call the listen method
        else:
            self.send() #if listen flag is not set, call the send method

    def send(self):
        self.socket.connect((self.args.target, self.args.port)) #connect to the specified target and port
        if self.buffer:
            self.socket.send(self.buffer) #send the buffer to the connected socket
        try:
            while True:
                recv_len = 1 #initialize the length of received data to 1
                response = '' #initialize the response to an empty string
                while recv_len: #while recv_len is not zero, keep receiving data
                    data = self.socket.recv(4096) #receive up to 4096 bytes of data from the socket
                    recv_len=len(data) #update recv_len to the length of the received data
                    response += data.decode() #decode the received data and append it to the response string
                    if recv_len<4096: #if the length of received data is less than 4096, break the loop
                        break
                if response: #if there is a response, print it
                    print(response, end='', flush=True) #print the response
                    buffer = input('> ') #prompt the user for input and store it in buffer
                    buffer += '\n' #add a newline character to the buffer
                    self.socket.send(buffer.encode()) #send the encoded buffer to the socket
        except KeyboardInterrupt: #if a keyboard interrupt is detected, close the socket and exit
            print('User terminated.')
            self.socket.close() #close the socket
            sys.exit() #exit the program

    def listen(self):
        self.socket.bind((self.args.target, self.args.port)) #bind the socket to the specified target and port
        self.socket.listen(5) #listen for incoming connections with a backlog of 5
        while True:
            client_socket, _ = self.socket.accept() #accept an incoming connection and get the client socketz
            client_thread= threading.Thread(target=self.handle, args=(client_socket,)) #create a new thread to handle the client connection
            client_thread.start() #start the client thread

    def handle(self, client_socket): 
        if self.args.execute: #if the execute flag is set, execute the specified command and send the output to the client socket
            output = execute(self.args.execute) #execute the command specified in the execute argument and store the output
            client_socket.send(output.encode()) #send the encoded output to the client socket   
        elif self.args.upload: #if the upload flag is set, receive the file data from the client socket and save it to the specified file
            file_buffer = b'' #initialize an empty byte string to store the file data
            while True: 
                data = client_socket.recv(4096) #receive up to 4096 bytes of data from the client socket
                if data:
                    file_buffer+= data
                else:
                    break
            with open(self.args.upload, 'wb') as f: #open the specified file in write-binary mode and save the received file data to it
                f.write(file_buffer) #write the received file data to the specified file
            message = f'saved file {self.args.upload}' #create a message indicating that the file has been saved
            client_socket.send(message.encode()) #send the encoded message to the client socket
        elif self.args.command: 
            cmd_buffer = b''
            client_socket.send(b'NC: #> ')
            while True:
                try:
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    client_socket.send(b'NC: #> ')
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Client connection dropped: {e}')
                    client_socket.close()
                    break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='python netcat',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
        netcat.py -t 192.168.1.108 -p 5555 -l -c #command shell
        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytext.txt #upload file
        netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" #execute command
        echo 'ABCDEFGHI' | ./netcat.py -t 192.168.1.108 -p 135 #echo text to server port 135
        netcat.py -t 192.168.1.108 -p 5555 #connect to server port 5555
        '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell') #if -c is specified, it will open a command shell
    parser.add_argument('-e', '--execute', help='execute specified command') #if -e is specified, it will execute the command
    parser.add_argument('-l', '--listen', action='store_true', help='listen') #if -l is specified, it will listen for incoming connections
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port') #specifies the port to listen on or connect to
    parser.add_argument('-t', '--target', default='', help='specified IP') #specifies the target IP address 
    parser.add_argument('-u', '--upload', help='upload file') #if -u is specified, it will upload the specified file
    args = parser.parse_args() #parse the command line arguments
    if args.listen:
        buffer='' #initialize buffer to empty string
    else:
        buffer = sys.stdin.read() #read from standard input and store in buffer
    nc = NetCat(args,buffer.encode()) #create an instance of NetCat class with the parsed arguments and encoded buffer
    nc.run() #call the run method of the NetCat instance to start the program