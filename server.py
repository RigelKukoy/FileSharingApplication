import socket
import os

# Configure server
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 5001
BUFFER_SIZE = 1024
SHARED_DIR = os.path.abspath('shared_files')  # Absolute path to shared_files

if not os.path.exists(SHARED_DIR):
    print(f"Error: Shared directory '{SHARED_DIR}' does not exist.")
    exit(1)

# Start server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)

print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}...")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        # Send the list of available files
        files = os.listdir(SHARED_DIR)
        files_list = "\n".join(files)
        client_socket.send(files_list.encode())

        # Receive the requested filename
        filename = client_socket.recv(BUFFER_SIZE).decode().strip()
        safe_filename = os.path.basename(filename)  # Sanitize file name
        filepath = os.path.join(SHARED_DIR, safe_filename)

        if os.path.exists(filepath):
            client_socket.send("FILE_FOUND".encode())
            with open(filepath, 'rb') as f:
                while (data := f.read(BUFFER_SIZE)):
                    client_socket.send(data)
            client_socket.send(b"EOF")  # End-of-file marker
            print(f"File '{safe_filename}' sent successfully.")
        else:
            client_socket.send("FILE_NOT_FOUND".encode())
            print(f"File '{safe_filename}' not found.")

        client_socket.close()

except KeyboardInterrupt:
    print("\nShutting down server...")
    server_socket.close()
