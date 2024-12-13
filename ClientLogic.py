import socket
import os
import threading
import time

class FileDownloadClient:
    def __init__(self, server_host='192.168.1.6', server_port=5001, buffer_size=1024):
        """
        Initialize the File Download Client
        
        :param server_host: IP address of the server
        :param server_port: Port number of the server
        :param buffer_size: Size of the buffer for network communication
        """
        self.SERVER_HOST = server_host
        self.SERVER_PORT = server_port
        self.BUFFER_SIZE = buffer_size
        self.download_status = {
            'status': None,  # None (not started), True (success), False (failed)
            'message': '',
            'timestamp': 0,
            'file_name': '',  # Track which file is being downloaded
            'progress': 0     # Progress percentage
        }
        self.download_lock = threading.Lock()
        self.is_downloading = False
        self.stop_download = False
    
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
    
    def _download_worker(self, selected_file):
        """
        Background worker for file download
        
        :param selected_file: Name of the file to download
        """
        try:
            with self.download_lock:
                # Reset download state and flags
                self.download_status = {
                    'status': None,
                    'message': f'Starting download of {selected_file}',
                    'timestamp': time.time(),
                    'file_name': selected_file,
                    'progress': 0
                }
                self.stop_download = False

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
                    
                    # Download file with progress tracking
                    total_bytes_received = 0
                    file_size = 0  # You might want to get actual file size from server

                    with open(filepath, 'wb') as f:
                        while not self.stop_download:
                            data = client_socket.recv(self.BUFFER_SIZE)
                            
                            # Break on end of file or stop signal
                            if data == b"EOF" or not data:
                                break
                            
                            f.write(data)
                            total_bytes_received += len(data)
                            
                            # Update progress (you'd need file size for accurate percentage)
                            with self.download_lock:
                                self.download_status['progress'] = min(100, total_bytes_received // 1024)
                    
                    # Wait for the DOWNLOAD_COMPLETE message
                    final_message = client_socket.recv(self.BUFFER_SIZE).decode()
                    
                    # Successfully downloaded
                    with self.download_lock:
                        self.download_status = {
                            'status': True,
                            'message': f"File '{selected_file}' downloaded successfully.",
                            'timestamp': time.time(),
                            'file_name': selected_file,
                            'progress': 100
                        }

                elif response == "FILE_NOT_FOUND":
                    # Update download status
                    with self.download_lock:
                        self.download_status = {
                            'status': False,
                            'message': f"File '{selected_file}' was not found on the server.",
                            'timestamp': time.time(),
                            'file_name': selected_file,
                            'progress': 0
                        }
                else:
                    # Update download status
                    with self.download_lock:
                        self.download_status = {
                            'status': False,
                            'message': "Invalid server response.",
                            'timestamp': time.time(),
                            'file_name': selected_file,
                            'progress': 0
                        }
        
        except Exception as e:
            # Update download status
            with self.download_lock:
                self.download_status = {
                    'status': False,
                    'message': f"An error occurred: {e}",
                    'timestamp': time.time(),
                    'file_name': selected_file,
                    'progress': 0
                }
        finally:
            with self.download_lock:
                self.is_downloading = False
    
    def download_file(self, selected_file):
        """
        Initiate file download in a background thread
        
        :param selected_file: Name of the file to download
        :return: Tuple (success, message)
        """
        if not selected_file:
            return False, "No file selected."
        
        if self.is_downloading:
            return False, "A download is already in progress."
        
        # Reset download status
        with self.download_lock:
            self.download_status = {
                'status': None,
                'message': f'Preparing download of {selected_file}',
                'timestamp': time.time(),
                'file_name': selected_file,
                'progress': 0
            }
        
        self.is_downloading = True
        
        # Start download in a separate thread
        download_thread = threading.Thread(
            target=self._download_worker, 
            args=(selected_file,)
        )
        download_thread.start()
        
        return True, "Download started."
    
    def check_download_status(self):
        """
        Check the current download status
        
        :return: Download status dictionary
        """
        with self.download_lock:
            # Return a copy of the status to prevent race conditions
            return dict(self.download_status)