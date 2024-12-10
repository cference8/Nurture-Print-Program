import os
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import sys

def resource_path(relative_path):
    """
    Get the absolute path to the resource, works for PyInstaller and dev mode.
    """
    try:
        # If the app is running as a PyInstaller bundle
        base_path = sys._MEIPASS
    except AttributeError:
        # If running in a normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def process_pdf(file_path, results, index):
    """
    Process the PDF file to swap the outside and inside pages and reverse the page order.
    The result is saved in the same directory as the input file.
    """
    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()

        # Swap the pages (2, 1), (4, 3), ..., etc.
        for i in range(0, len(reader.pages), 2):
            if i + 1 < len(reader.pages):
                writer.add_page(reader.pages[i + 1])  # Inside page
            writer.add_page(reader.pages[i])  # Outside page

        # Reverse the page order
        reversed_writer = PdfWriter()
        for i in range(len(writer.pages)):
            reversed_writer.add_page(writer.pages[len(writer.pages) - 1 - i])

        # Modify the output file name
        file_name, file_ext = os.path.splitext(os.path.basename(file_path))  # Separate name and extension
        output_file_name = f"{file_name}_Reordered{file_ext}"  # Append "_Reordered" before the extension
        output_path = os.path.join(os.path.dirname(file_path), output_file_name)  # Full path

        # Save the processed file
        with open(output_path, "wb") as output_file:
            reversed_writer.write(output_file)

        results[index] = f"Processed: {output_path}"  # Save the success result
    except Exception as e:
        results[index] = f"Error processing file '{file_path}': {str(e)}"  # Save the error


def process_multiple_files(file_paths):
    """
    Process multiple PDF files using multithreading.
    """
    threads = []
    results = [None] * len(file_paths)  # Placeholder for results

    # Create and start a thread for each file
    for i, file_path in enumerate(file_paths):
        thread = threading.Thread(target=process_pdf, args=(file_path, results, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Display results to the user
    success_files = [res for res in results if res and "Error" not in res]
    error_files = [res for res in results if res and "Error" in res]

    if success_files:
        messagebox.showinfo("Success", f"Processed files:\n" + "\n".join(success_files))
    if error_files:
        messagebox.showwarning("Errors", f"Failed to process the following files:\n" + "\n".join(error_files))


def select_files():
    """
    Open a file dialog to select multiple PDF files for processing.
    """
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    if file_paths:
        process_multiple_files(file_paths)


def drop_event(event):
    """
    Handle drag-and-drop events for multiple PDF files.
    """
    # Extract and clean raw paths
    raw_file_paths = event.data.strip()
    print(f"Raw file paths: {raw_file_paths}")  # Debug print

    # Split paths correctly
    file_paths = raw_file_paths.split("} {")  # Split on "} {" for multiple files
    cleaned_file_paths = []

    for path in file_paths:
        # Clean up leading/trailing braces or whitespace
        normalized_path = os.path.normpath(path.strip().strip("{}"))
        print(f"Normalized path: {normalized_path}")  # Debug print
        
        # Validate the path
        if os.path.isfile(normalized_path):
            cleaned_file_paths.append(normalized_path)
        else:
            print(f"Invalid path detected: {normalized_path}")  # Debug print

    # Check if valid files are found
    if cleaned_file_paths:
        process_multiple_files(cleaned_file_paths)
    else:
        messagebox.showwarning("Invalid Input", "No valid PDF files were provided.")


# GUI Setup
ctk.set_appearance_mode("System")  # Options: "System", "Light", "Dark"
ctk.set_default_color_theme("blue")  # Color theme

# Use TkinterDnD for drag-and-drop support
app = TkinterDnD.Tk()
app.title("PDF Page Reorder")
app.geometry("400x300")

# Set application icon
app.iconbitmap(resource_path("scribe-icon.ico"))

# Load and add logo image
logo_image = ctk.CTkImage(
    light_image=Image.open(resource_path("scribe-logo-final.webp")),  # Use light theme image
    dark_image=Image.open(resource_path("scribe-logo-final.webp")),  # Same for dark theme
    size=(200, 100),  # Resize the logo to fit the space
)

# Add logo label
logo_label = ctk.CTkLabel(app, image=logo_image, text="")
logo_label.pack(pady=(10, 30))  # Add padding below the logo

# Main Frame
frame = ctk.CTkFrame(app, width=400, height=200, corner_radius=15, fg_color="#123524")
frame.pack(pady=(0, 20))  # Add padding to separate from the logo

# Drag-and-Drop Label
drag_drop_label = ctk.CTkLabel(
    frame,
    text="Drag & Drop Files to Upload\n\nOR",
    font=ctk.CTkFont(size=16, weight="bold"),
    text_color="gray",
)
drag_drop_label.pack(pady=20, padx=20)

# Browse Files Button
browse_button = ctk.CTkButton(
    frame,
    text="Browse Files",
    command=select_files,
    width=150,
    height=40,
    corner_radius=8,
    font=ctk.CTkFont(size=16, weight="bold"),
)
browse_button.pack(pady=10)

# Enable drag-and-drop support
app.drop_target_register(DND_FILES)
app.dnd_bind("<<Drop>>", drop_event)

# Run the GUI
app.mainloop()
