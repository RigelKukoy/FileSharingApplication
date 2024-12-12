import socket
import os

# Configure server
SERVER_HOST = '172.20.10.14'  
SERVER_PORT = 5001
BUFFER_SIZE = 1024

# Create shared_files directory if it doesn't exist
SHARED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared_files')
os.makedirs(SHARED_DIR, exist_ok=True)

# Start server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(5)

print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}...")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        try:
            # Send the list of available files
            files = os.listdir(SHARED_DIR)
            files_list = "\n".join(files) if files else "No files available"
            client_socket.send(files_list.encode())

            # Receive the requested filename
            filename = client_socket.recv(BUFFER_SIZE).decode().strip()
            if not filename:
                client_socket.send("INVALID_REQUEST".encode())
                print(f"Invalid file request from {client_address}")
                continue

            safe_filename = os.path.basename(filename)  # Sanitize file name
            filepath = os.path.join(SHARED_DIR, safe_filename)

            if os.path.exists(filepath):
                client_socket.send("FILE_FOUND".encode())
                print(f"File '{safe_filename}' found, preparing to send.")

                # Send the file
                with open(filepath, 'rb') as f:
                    while (data := f.read(BUFFER_SIZE)):
                        client_socket.send(data)
                client_socket.send(b"EOF")  # End-of-file marker
                print(f"File '{safe_filename}' sent successfully.")
            else:
                client_socket.send("FILE_NOT_FOUND".encode())
                print(f"File '{safe_filename}' not found.")

        except Exception as e:
            print(f"Error processing client request: {e}")
        finally:
            client_socket.close()

except KeyboardInterrupt:
    print("\nShutting down server...")
    server_socket.close()
