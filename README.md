# Python Netcat

A lightweight Python reimplementation of core netcat functionality, built for network communication, remote command execution, and file transfer during security testing and lab exercises.

## Features

- Connect to or listen on a specified host and port
- Execute a single command and return output to a connected client
- Spawn an interactive command shell over the connection
- Upload files from a client to the listener
- Pipe data via stdin for simple data transfer

## Usage

```bash
# Interactive command shell
python netcat.py -t 192.168.1.108 -p 5555 -l -c

# Upload a file to the listener
python netcat.py -t 192.168.1.108 -p 5555 -l -u=mytext.txt

# Execute a single command
python netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd"

# Send piped input to a remote port
echo 'ABCDEFGHI' | python netcat.py -t 192.168.1.108 -p 135

# Connect as a client
python netcat.py -t 192.168.1.108 -p 5555
```

## Options

| Flag | Description |
|------|-------------|
| `-l, --listen` | Listen for incoming connections |
| `-c, --command` | Open an interactive command shell |
| `-e, --execute` | Execute a specified command |
| `-u, --upload` | Receive and save an uploaded file |
| `-t, --target` | Target IP address |
| `-p, --port` | Target/listen port (default: 5555) |

## How It Works

- Built on Python's `socket` module using a single TCP stream (`AF_INET`, `SOCK_STREAM`).
- `SO_REUSEADDR` is set on the listening socket to allow immediate rebinding after restart.
- Each incoming client connection is handled in its own `threading.Thread`, so the listener supports multiple concurrent clients.
- Data is read in 4096-byte chunks until a smaller chunk signals end of transmission; the command-shell mode instead reads until a newline is seen, treating each line as one command.
- Command execution runs through `subprocess.check_output` with `shlex.split`, capturing stdout and stderr and returning the result as text.
- Client mode reads from `stdin` at startup, sends it once connected, then drops into an interactive receive/prompt loop until `Ctrl+C`.

## Requirements

- Python 3.x, standard library only (no external dependencies)

## Disclaimer

This tool is intended for authorized security testing, CTFs, and lab environments only. Use against systems you do not own or have explicit permission to test is illegal.
