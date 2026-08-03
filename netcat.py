#comments are added for my understanding and learning purposes.
import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip() #remove leading and trailing whitespace
    if not cmd: #if command is empty
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT) #shlex.split(): safely parses the command string into a list formatted for OS execution and stderr=subprocess.STDOUT: forces error output into the same string stream as standard output.
    return output.decode() #return decoded output

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