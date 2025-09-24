# Allodatr: ALlodatr LOcal DAta TRansfer
import socket
import time
import sys
import os

serverside = input('Server [y/]? ').strip().lower()=='y'
homeport = 4110
clienttimeout = 3
servertimeout = 60
maintimeout = 10

# header byte:
# 0000000a
# a: 1 for file, 0 for message

phonebook = [['localhost',-1,0],['192.168.178.54',-1,0],['192.168.0.120',-1,0],['192.168.0.118',-1,0]] # (ip, mostrecentsuccess)

def buildmessage(s):
    header = 0 | 0
    bytestr = s.encode('utf-8')
    size = len(bytestr)
    return header.to_bytes(1,'little')+size.to_bytes(4,'little')+bytestr

def checkphonebook():
    for i, entry in enumerate(phonebook):
        ip = entry[0]
        port = entry[1]
        if port == -1:
            port = homeport
        print(f"Testing {ip}:{port}...")
        try:
            result = -1
            testsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            testsock.settimeout(clienttimeout)
            result = testsock.connect_ex((ip, port))
        except Exception: # Isn't run if successful, catches control+c
            print('ERROR!')
            testsock.close()
        else:
            if result == 0:
                print(f"Success! Connected to {ip}:{port}.")
                
                # Code checking is socket is willing
                
                phonebook[i][2] = time.time()
                return testsock
            testsock.close()
    print("No socket found.")
    return None
    
    

if __name__=="__main__":
    # Get local IP
    hostname = socket.gethostname()
    localip = socket.gethostbyname(hostname)
    print(f'\n{localip}\nHostname: {hostname}\n')
    if serverside:
        try:
            print(f"Running as server on port {homeport}.")
            serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversock.bind(('', homeport))
            
            serversock.listen(1)
            serversock.settimeout(servertimeout)
        except Exception:
            serversock.close()
            print("FAILURE: Error on creating server socket.")
            sys.exit(0)
        
        try:
            sock, addr = serversock.accept()
            ip, _ = addr
            phonebook += [ip, homeport, time.time()]
        except socket.timeout:
            serversock.close()
            print("FAILURE: Socket timed out.")
            sys.exit(0)
        except Exception as e:
            serversock.close()
            sock.close()
            print("FAILURE: Error on accepting.")
            print(e)
            sys.exit(0)
        serversock.close()
        print(f"Success! Connected to {ip}")
         
            
    else:
        print("Running as client.")
        sock = checkphonebook()
        if sock is None:
            # Look for alternative connection.
            print("FAILURE: No socket found. Quitting.")
            sys.exit(0)
    
    sock.settimeout(maintimeout)
    while True:
        while True:
            resp = input("[L]isten, [S]end, [U]pload or [Q]uit? ").strip().upper()
            if resp == 'L' or resp == 'S' or resp == 'U' or resp == 'Q':
                break
            print("Didn't get that.")
        if resp == 'Q':
            sock.close()
            sys.exit()
        elif resp == 'L':
            preamble = sock.recv(5)
            if preamble == b'':
                print('Connection broken.')
                sock.close()
                sys.exit(0)
            header = preamble[0]
            size = int.from_bytes(preamble[1:5],'little')
            
            if size > 0:
                if header&1:
                    # File.
                    print('A file has been sent.')
                    if input('Accept [y/]? ').strip().lower() != 'y':
                        print('Discarding file.')
                        bytes_recd = 0
                        while bytes_recd < size:
                            if sock.recv(min(size-bytes_recd,65536*8)) == b'':
                                print('Connection broken.')
                                sock.close()
                                sys.exit(0)
                        bytes_recd += len(chunk)
                    filename = input('Save as? ')
                    consolemode = filename == ''
                    
                    with open(filename, 'wb') as f:
                        bytes_recd = 0
                        print('Size:')
                        print(size)
                        while bytes_recd < size:
                            for _ in range(16):
                                chunk = sock.recv(min(size-bytes_recd,65536*8))
                                if chunk == b'':
                                    print('Connection broken.')
                                    sock.close()
                                    sys.exit(0)
                                f.write(chunk)
                                bytes_recd += len(chunk)
                                if bytes_recd >= size:
                                    break
                            print(bytes_recd>>20,end='\r')
                    print(f'Done. Wrote {size} bytes to {filename}.')
                else:
                    print()
                    # Message
                    chunks = []
                    bytes_recd = 0
                    while bytes_recd < size:
                        chunk = sock.recv(min(size-bytes_recd,2048))
                        if chunk == b'':
                            print('Connection broken.')
                            sock.close()
                            sys.exit(0)
                        chunks.append(chunk)
                        bytes_recd += len(chunk)
                    rawmsg = b''.join(chunks)
                    msg = rawmsg.decode('utf-8')
                    print(msg)
                    print()
            else:
                print(f"size={size} (no ")
                    
        elif resp == 'S':
            msg = ''
            while True:
                line = input(' > ')
                if line == '':
                    break
                if msg:
                    msg += '\n'
                msg += line
            rawmsg = buildmessage(msg)
            rawmsglen = len(rawmsg)
            
            bytes_sent = 0
            while bytes_sent < rawmsglen:
                sent = sock.send(rawmsg[bytes_sent:min(rawmsglen,2048+bytes_sent)])
                if sent == 0:
                    print('Connection broken.')
                    sock.close()
                    sys.exit(0)
                bytes_sent += sent
        elif resp == 'U':
            filename = input('Filename? ')
            if not os.path.exists(filename):
                print('Can\'t find file.')
            else:
                size = os.path.getsize(filename)
                print('Size:')
                print(size>>20)
                bytes_read = 0
                
                header = 1
                
                preamble = sock.send(header.to_bytes(1,'little')+size.to_bytes(4,'little'))
                if preamble == 0:
                    print('Connection broken.')
                    sock.close()
                    sys.exit(0)
                    
                
                with open(filename, 'rb') as f:
                    while bytes_read < size:
                        for _ in range(16):
                            chunk = f.read(min(size-bytes_read, 65536*8))
                            sent = sock.send(chunk)
                            if sent == 0:
                                print('Connection broken.')
                                sock.close()
                                sys.exit(0)
                            bytes_read += sent
                            if bytes_read >= size:
                                break
                        print(bytes_read>>20,end='\r')
                    
                    
                    
