import socket
import os
import tkinter.messagebox as messagebox

class FileDownloadClient:
    def __init__(self, server_host='172.20.10.14', server_port=5001, buffer_size=1024):
        """
        Initialize the File Download Client
        
        :param server_host: IP address of the server
        :param server_port: Port number of the server
        :param buffer_size: Size of the buffer for network communication
        """
        self.SERVER_HOST = server_host
        self.SERVER_PORT = server_port
        self.BUFFER_SIZE = buffer_size
    
    def get_file_list(self):
        """
        Retrieve the list of files from the server
        
        :return: List of files or None if connection fails
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
                files_list = client_socket.recv(self.BUFFER_SIZE).decode()
                return files_list.split('\n')
        except Exception as e:
            print(f"Error retrieving file list: {e}")
            return None
    
    def download_file(self, selected_file):
        """
        Download a specific file from the server
        
        :param selected_file: Name of the file to download
        :return: Tuple (success, message)
        """
        if not selected_file:
            return False, "No file selected."
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.SERVER_HOST, self.SERVER_PORT))
                
                # Receive the file list (part of protocol)
                client_socket.recv(self.BUFFER_SIZE).decode()
                
                # Send the file name
                client_socket.send(selected_file.encode())
                
                # Receive server response
                response = client_socket.recv(self.BUFFER_SIZE).decode()
                
                if response == "FILE_FOUND":
                    # Ensure downloads directory exists
                    filepath = os.path.join("downloads", selected_file)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Download file
                    with open(filepath, 'wb') as f:
                        while True:
                            data = client_socket.recv(self.BUFFER_SIZE)
                            if data == b"EOF":  # End-of-file marker
                                break
                            f.write(data)
                    
                    return True, f"File '{selected_file}' downloaded successfully."
                elif response == "FILE_NOT_FOUND":
                    return False, f"File '{selected_file}' was not found on the server."
                else:
                    return False, "Invalid server response."
        
        except Exception as e:
            return False, f"An error occurred: {e}"