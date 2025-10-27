# File Telnet Server

A simple telnet server that allows clients to browse files and directories in a secure, sandboxed environment.

## How to Run

### Prerequisites
- Python 3.6 or higher

### Running the Server

1. **Basic usage (current directory as root):**
   ```bash
   python3 telnet_file.py
   ```
   When prompted, press Enter to use the current directory, or specify a path.

2. **Specify root directory as command line argument:**
   ```bash
   python3 telnet_file.py /path/to/your/directory
   ```

3. **Example:**
   ```bash
   python3 telnet_file.py /home/user/Documents
   ```

### Connecting to the Server

Once the server is running, you can connect using any telnet client:

```bash
telnet localhost 2323
```

### Available Commands

- `ls [path]` - List directory contents
- `cd [path]` - Change directory
- `cat <file>` - Display file contents
- `pwd` - Show current directory
- `help` - Show help message
- `quit` or `exit` - Disconnect from server

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Security Note

The server only allows access to files within the specified root directory. Clients cannot access files outside this sandboxed environment.