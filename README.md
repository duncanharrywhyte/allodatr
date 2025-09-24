# Allodatr - Local Data Transfer

**AL**lodatr **LO**cal **DA**ta **TR**ansfer is a Python-based application for transferring files and messages between computers on a local network using socket connections.

## Features

- **Dual Mode Operation**: Run as either server or client
- **File Transfer**: Upload and download files between connected computers
- **Message Exchange**: Send and receive text messages
- **Network Discovery**: Automatically discover available connections using a built-in phonebook
- **Real-time Progress**: Progress indicators for file transfers
- **Cross-platform**: Works on any system with Python

## Requirements

- Python 3.6 or higher
- Network connectivity between machines

## Installation

1. Clone or download this repository
2. Ensure Python 3.6+ is installed on your system
3. No additional dependencies required (uses only standard library)

## Usage

### Starting the Application

```bash
python allodatr.py
```

When prompted, choose your mode:
- Enter `y` to run as **Server** (waits for connections)
- Press Enter to run as **Client** (connects to available servers)

### Available Commands

Once connected, you can use the following commands:

- **`L`** - **Listen**: Wait for incoming messages or files
- **`S`** - **Send**: Send a text message to the connected peer
- **`U`** - **Upload**: Send a file to the connected peer
- **`Q`** - **Quit**: Close the connection and exit

### Configuration

The application includes a built-in phonebook with common local IP addresses:
- `localhost`
- `192.168.178.54`
- `192.168.0.120`
- `192.168.0.118`

You can modify the `phonebook` list in the source code to add your own network addresses.

### Network Settings (defaults)

- **Default Port**: 4110
- **Client Timeout**: 3 seconds
- **Server Timeout**: 60 seconds
- **Main Timeout**: 10 seconds

## How It Works

1. **Server Mode**: Creates a socket server that listens for incoming connections
2. **Client Mode**: Attempts to connect to known addresses in the phonebook
3. **Communication**: Uses a simple protocol with headers to distinguish between messages and files
4. **File Transfer**: Handles large file transfers in chunks with progress indicators

## Protocol Details

The application uses a simple binary protocol:
- **Header**: 1 byte (bit 0: 1 for file, 0 for message)
- **Size**: 4 bytes (little-endian integer)
- **Data**: Variable length payload

## Security Note

This application is designed for use on trusted local networks only. It does not include encryption or authentication mechanisms.

## Troubleshooting

- **"No socket found"**: Ensure the server is running and reachable on the network
- **Connection timeouts**: Check firewall settings and network connectivity
- **Port conflicts**: Modify the `homeport` variable if port 4110 is in use