import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
import time
import os
from ClientLogic import FileDownloadClient

class FileDownloadApp(ctk.CTk):
    def __init__(self):
        """Initialize the File Download Application"""
        # Use CustomTkinter initialization
        super().__init__()
        
        # Set color theme before creating widgets
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure application window
        self.title("Modern File Downloader")
        self.geometry("500x650")
        
        # Create network client
        self.client = FileDownloadClient()
        
        # Track last known download status
        self.last_status_timestamp = 0
        
        # Set up user interface
        self._setup_main_frame()
        self._setup_title()
        self._setup_file_list()
        self._setup_control_buttons()
        self._setup_status_label()
        
        # Initial file list refresh
        self._refresh_file_list()
        
        # Set up periodic download status check
        self._download_status_check()
    
    def _setup_main_frame(self):
        """Create the main container frame"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(
            pady=20, 
            padx=20, 
            fill="both", 
            expand=True
        )
    
    def _setup_title(self):
        """Create and position the application title"""
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="File Downloader", 
            font=("Roboto", 24, "bold")
        )
        self.title_label.pack(
            pady=(20, 10)
        )
    
    def _setup_file_list(self):
        """Create the file list container and listbox"""
        # List container
        self.list_frame = ctk.CTkScrollableFrame(
            self.main_frame, 
            width=400, 
            height=300
        )
        self.list_frame.pack(
            pady=10, 
            padx=10, 
            fill="both", 
            expand=True
        )
        
        # Listbox for files
        self.file_listbox = tk.Listbox(
            self.list_frame, 
            width=50, 
            height=15,
            bg='#2b2b2b',  # Dark background to match CustomTkinter
            fg='white',    # White text
            selectbackground='#1f6aa5',  # Highlight color
            selectforeground='white'
        )
        self.file_listbox.pack(
            pady=10, 
            padx=10, 
            fill="both", 
            expand=True
        )
    
    def _setup_control_buttons(self):
        """Create refresh and download buttons"""
        # Button container
        self.button_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="transparent"
        )
        self.button_frame.pack(
            pady=10, 
            padx=10, 
            fill="x"
        )
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.button_frame, 
            text="Refresh File List", 
            command=self._refresh_file_list,
            corner_radius=10
        )
        self.refresh_button.pack(
            side="left", 
            expand=True, 
            padx=5
        )
        
        # Download button
        self.download_button = ctk.CTkButton(
            self.button_frame, 
            text="Download File", 
            command=self._download_file,
            corner_radius=10,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.download_button.pack(
            side="right", 
            expand=True, 
            padx=5
        )
    
    def _setup_status_label(self):
        """Create a status label to show download progress"""
        self.status_label = ctk.CTkLabel(
            self.main_frame, 
            text="",
            font=("Roboto", 14)
        )
        self.status_label.pack(
            pady=10
        )
    
    def _refresh_file_list(self):
        """
        Refresh the list of files from the server
        
        Handles clearing existing list and populating with new files
        """
        try:
            # Clear existing items
            self.file_listbox.delete(0, tk.END)
            
            # Retrieve and display files
            files = self.client.get_file_list()
            
            if files:
                # Add non-empty files to listbox
                for file in files:
                    if file and file.strip():
                        self.file_listbox.insert(tk.END, file)
            else:
                # Show error if no files retrieved
                messagebox.showerror(
                    "Error", 
                    "Could not retrieve file list."
                )
        
        except Exception as e:
            # Handle any connection or retrieval errors
            messagebox.showerror(
                "Error", 
                f"Connection error: {e}"
            )
    
    def _download_file(self):
        """
        Download the selected file
        
        Validates file selection and handles download process
        """
        try:
            # Validate file selection
            selected_indices = self.file_listbox.curselection()
            
            if not selected_indices:
                messagebox.showerror(
                    "Error", 
                    "Please select a file to download."
                )
                return
            
            # Get selected file name
            selected_file = self.file_listbox.get(selected_indices[0])
            
            # Attempt file download
            success, message = self.client.download_file(selected_file)
            
            # Update status label
            if success:
                self.status_label.configure(text=f"Downloading: {selected_file}", text_color="white")
            else:
                self.status_label.configure(text=message, text_color="red")
        
        except Exception as e:
            # Handle any unexpected errors
            messagebox.showerror(
                "Error", 
                f"An unexpected error occurred: {e}"
            )
    
    def _download_status_check(self):
        """
        Periodically check download status and display results
        """
        # Check current download status
        status = self.client.check_download_status()
        
        # Only process if status has changed and is not None
        if (status['status'] is not None and 
            status['timestamp'] > self.last_status_timestamp):
            
            # Update last known timestamp
            self.last_status_timestamp = status['timestamp']
            
            # Update status label
            if status['status']:
                self.status_label.configure(
                    text=status['message'], 
                    text_color="green"
                )
                # Show success message box
                messagebox.showinfo("Download Complete", status['message'])
            else:
                self.status_label.configure(
                    text=status['message'], 
                    text_color="red"
                )
                # Show error message box
                messagebox.showerror("Download Error", status['message'])
        
        # Schedule next check (reduced interval for more responsive updates)
        self.after(200, self._download_status_check)

def main():
    """Create and run the application"""
    # Ensure downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    
    # Create and run the application
    app = FileDownloadApp()
    app.mainloop()

if __name__ == "__main__":
    main()