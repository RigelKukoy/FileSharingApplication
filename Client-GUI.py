import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as messagebox
from ClientLogic import FileDownloadClient

class FileDownloadApp(ctk.CTk):
    def __init__(self):
        """Initialize the File Download Application"""
        super().__init__()
        
        # Configure application appearance
        self._configure_appearance()
        
        # Create network client
        self.client = FileDownloadClient()
        
        # Set up user interface
        self._create_main_layout()
        self._create_title()
        self._create_file_list()
        self._create_control_buttons()
        
        # Initial file list refresh
        self.refresh_file_list()
    
    def _configure_appearance(self):
        """Set up application visual settings"""
        self.title("Modern File Downloader")
        self.geometry("500x600")
        
        # Set color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def _create_main_layout(self):
        """Create the main container frame"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(
            pady=20, 
            padx=20, 
            fill="both", 
            expand=True
        )
    
    def _create_title(self):
        """Create and position the application title"""
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="File Downloader", 
            font=("Roboto", 24, "bold")
        )
        self.title_label.pack(
            pady=(20, 10)
        )
    
    def _create_file_list(self):
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
    
    def _create_control_buttons(self):
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
            command=self.refresh_file_list,
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
            command=self.download_file,
            corner_radius=10,
            fg_color="green"
        )
        self.download_button.pack(
            side="right", 
            expand=True, 
            padx=5
        )
    
    def refresh_file_list(self):
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
                    if file.strip():
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
    
    def download_file(self):
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
            
            # Show appropriate message based on download result
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
        
        except Exception as e:
            # Handle any unexpected errors
            messagebox.showerror(
                "Error", 
                f"An unexpected error occurred: {e}"
            )

def main():
    """Create and run the application"""
    app = FileDownloadApp()
    app.mainloop()

if __name__ == "__main__":
    main()