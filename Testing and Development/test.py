import customtkinter as ctk
import base64
from PIL import Image
from io import BytesIO
import CTkMessagebox as msg
import webbrowser
import os
import sys
import subprocess
import winreg as reg
from datetime import datetime as dt
import tkinter.filedialog as fd

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

reg_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"

password = "password"

# Project information html file path function
def resource_path(relative_path):

    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def project_info():

    """ Opens the project information HTML file in the default web browser. """

    path = resource_path("project_info.html")
    webbrowser.open(f"file://{os.path.abspath(path)}")

# Function to log actions to a file
def log_action(action):

    """ Logs actions to a file with a timestamp. """

    log_file = "usb_log.txt"
    with open(log_file, "a") as file:
        timestamp = dt.now().strftime("%d-%m-%Y %H:%M:%S")
        file.write(f"{timestamp} - {action}\n")

# Function to check USB port status
def usb_status():

    """ Checks the status of USB ports by reading the registry key. """

    try:
        with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, reg_path) as key:
            value, _ = reg.QueryValueEx(key, "Start") #value,_ throw away variable, donot want the type_of_data from the returning tuple
        if value == 3:
            status = "USB ports are Enabled"
            msg.CTkMessagebox(title="USB Status", message="USB Storage Devices are Enabled", icon="check", option_1="OK")
        elif value == 4:
            status = "USB ports are Disabled"
            msg.CTkMessagebox(title="USB Status", message="USB Storage Devices are Disabled", icon="cancel", option_1="OK")
        else:
            msg.CTkMessagebox(title="USB Status", message="USB Storage Devices status is unknown", icon="warning", option_1="OK")
    except FileNotFoundError:
        msg.CTkMessagebox(title="Error", message="USBSTOR registry key not found. Please run the application as an administrator.", icon="cancel", option_1="OK")
    except Exception as e:
        msg.CTkMessagebox(title="Error", message=f"An unexpected error occurred: {str(e)}", icon="cancel", option_1="OK")
    
    log_action(f'Checked USB status : {status}') # Write the action to log file

# Log button functionality
def open_log():

    """ Opens the USB log window with search and filter functionality. """

    def filter_log(*args):

        """ Filters the log content based on search term and selected type. """

        search_term = search_var.get().lower()
        selected_type = filter_var.get()
        filtered = []

        for line in reversed(log_content):
            matches_search = search_term in line.lower()
            matches_type = (
                selected_type == "All" or
                (selected_type == "Enabled" and "enabled" in line.lower()) or
                (selected_type == "Disabled" and "disabled" in line.lower()) or
                (selected_type == "Checked" and "checked" in line.lower()) or
                (selected_type == "Cleared" and "cleared" in line.lower())
            )
            if matches_search and matches_type:
                filtered.append(line)

        update_log_text(filtered)

    def update_log_text(lines):

        """ Updates the log text area with the provided lines. """

        log_text.configure(state="normal")
        log_text.delete("0.0", "end")
        log_text.insert("0.0", "\n".join(lines))
        log_text.configure(state="disabled")

    def export_log():

        """ Exports the log content to a text file. """

        export_path = fd.asksaveasfilename(defaultextension=".txt",filetypes=[("Text files", "*.txt")],title="Export Log As")
        if export_path:
            with open(export_path, "w") as e_file:
                e_file.write("\n".join(log_content))
            msg.CTkMessagebox(title="Export Log",message=f"Log exported to:\n{export_path}",icon="check",option_1="OK")

    def secure_clear_log():

        """ Clears the log content securely by overwriting it with a note. """

        timestamp = dt.now().strftime("%d-%m-%Y %H:%M:%S")
        secure_note = f"{timestamp} - Log cleared (secure action)"
        log_content.clear()
        log_content.append(secure_note)
        with open("usb_log.txt", "w") as file:
            file.write("\n".join(log_content) + "\n")
        update_log_text(reversed(log_content))

    # Load log file
    try:
        with open("usb_log.txt", "r") as file:
            log_content = file.read().strip().splitlines()
    except FileNotFoundError:
        log_content = ["Log file not found. No actions have been logged yet."]

    log_window = ctk.CTkToplevel()
    log_window.title("USB Log")
    log_window.geometry("750x520")

    # Search and filter controls
    control_frame = ctk.CTkFrame(master=log_window)
    control_frame.pack(padx=15, pady=(10, 5), fill="x")

    search_var = ctk.StringVar()
    search_var.trace_add("write", filter_log)
    search_entry = ctk.CTkEntry(master=control_frame, textvariable=search_var, placeholder_text="Search log...")
    search_entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)

    filter_var = ctk.StringVar(value="All")
    filter_options = ["All", "Enabled", "Disabled", "Checked", "Cleared"]
    filter_dropdown = ctk.CTkOptionMenu(master=control_frame, variable=filter_var, values=filter_options,command=lambda _: filter_log())
    filter_dropdown.pack(side="left", padx=10)

    # Log display with scrollbar
    log_frame = ctk.CTkFrame(master=log_window)
    log_frame.pack(padx=15, pady=5, fill="both", expand=True)

    log_text = ctk.CTkTextbox(master=log_frame, wrap="word", state="normal", font=("Consolas", 12), fg_color="#2c2f33",
        text_color="white", border_color="#7289da", border_width=1, corner_radius=5)
    log_text.grid(row=0, column=0, sticky="nsew")

    log_scrollbar = ctk.CTkScrollbar(master=log_frame, command=log_text.yview)
    log_text.configure(yscrollcommand=log_scrollbar.set)
    log_scrollbar.grid(row=0, column=1, sticky="ns")

    log_frame.grid_rowconfigure(0, weight=1)
    log_frame.grid_columnconfigure(0, weight=1)

    update_log_text(reversed(log_content))

    # Bottom button section
    button_frame = ctk.CTkFrame(master=log_window, fg_color="transparent")
    button_frame.pack(pady=10)

    clear_button = ctk.CTkButton(master=button_frame, text="Clear Log (Secure)",hover_color="#d15a15", command=secure_clear_log)
    clear_button.pack(side="left", padx=10)

    export_button = ctk.CTkButton(master=button_frame, text="Export Log",hover_color="#d15a15", command=export_log)
    export_button.pack(side="left", padx=10)

    close_button = ctk.CTkButton(master=button_frame, text="Close",hover_color="#d15a15", command=log_window.destroy)
    close_button.pack(side="left", padx=10)

# Function to enable USB ports
def con_button_clicked():

    """ Opens a password entry window to enable USB ports. """

    password_window = ctk.CTkToplevel()
    password_window.title("Enter Password")
    password_window.geometry("400x200")
    password_frame = ctk.CTkFrame(master=password_window)
    password_frame.pack(pady=10, padx=20, fill="both", expand=True)
    password_label = ctk.CTkLabel(master=password_frame, text="Enter Password:")
    password_label.pack(pady=5)
    password_entry = ctk.CTkEntry(master=password_frame, show="*")
    password_entry.pack(pady=5)
    show_password = ctk.CTkCheckBox(master=password_frame, text="Show Password",checkbox_height= 20,checkbox_width=20 ,command=lambda: password_entry.configure(show="" if show_password.get() else "*"))
    show_password.pack(pady=1)
    button_frame = ctk.CTkFrame(master=password_frame)
    button_frame.pack(pady=10)

    failed_attempts = [0] #list to avoid unbound local variable error as python does not allow to modify outer variable in inner function

    def check_password():

        """ Checks the entered password and enables USB ports if correct. """

        if password_entry.get() == password:
            subprocess.run([r'enable_usb.bat'], shell=True)
            log_action('Enabled USB Ports')
            password_window.destroy()
            msg.CTkMessagebox(title="Success", message="USB Storage Devices Enabled", icon="check", option_1="OK")
        else:
            failed_attempts[0] += 1
            log_action(f'Incorrect Password Attempt to enable USB ports, Attempt - {failed_attempts[0]}')
            msg.CTkMessagebox(title="Error", message="Incorrect Password", icon="cancel", option_1="OK")
            password_entry.delete(0, ctk.END)

    submit_button = ctk.CTkButton(master=button_frame, text="Submit", fg_color="#0ecc3e", text_color= "black", hover_color="#d15a15", command=check_password)
    submit_button.grid(pady=10,padx=5, row=0, column=0)
    cancel_button = ctk.CTkButton(master=button_frame, text="Cancel",fg_color="#a31735", text_color= "black", hover_color="#d15a15" ,command=password_window.destroy)
    cancel_button.grid(pady=10, padx=5, row=0, column=1)

# Function to disable USB ports
def discon_button_clicked():

    """ Opens a password entry window to disable USB ports. """

    password_window = ctk.CTkToplevel()
    password_window.title("Enter Password")
    password_window.geometry("400x200")
    password_frame = ctk.CTkFrame(master=password_window)
    password_frame.pack(pady=10, padx=20, fill="both", expand=True)
    password_label = ctk.CTkLabel(master=password_frame, text="Enter Password:")
    password_label.pack(pady=5)
    password_entry = ctk.CTkEntry(master=password_frame, show="*")
    password_entry.pack(pady=5)
    show_password = ctk.CTkCheckBox(master=password_frame, text="Show Password",checkbox_height= 20,checkbox_width=20 ,command=lambda: password_entry.configure(show="" if show_password.get() else "*"))
    show_password.pack(pady=1)
    button_frame = ctk.CTkFrame(master=password_frame)
    button_frame.pack(pady=10)

    failed_attempts = [0]

    def check_password():

        """ Checks the entered password and disables USB ports if correct. """

        if password_entry.get() == password:
            subprocess.run([r'disable_usb.bat'], shell=True)
            log_action('Disabled USB Ports')
            password_window.destroy()
            msg.CTkMessagebox(title="Success", message="USB Storage Devices Disabled", icon="check", option_1="OK")
        else:
            failed_attempts[0] += 1
            log_action(f'Incorrect Password Attempt to enable USB ports, Attempt - {failed_attempts[0]}')
            msg.CTkMessagebox(title="Error", message="Incorrect Password", icon="cancel", option_1="OK")
            password_entry.delete(0, ctk.END)

    submit_button = ctk.CTkButton(master=button_frame, text="Submit", fg_color="#0ecc3e", text_color= "black", hover_color="#d15a15", command=check_password)
    submit_button.grid(pady=10,padx=5, row=0, column=0)
    cancel_button = ctk.CTkButton(master=button_frame, text="Cancel",fg_color="#a31735", text_color= "black", hover_color="#d15a15" ,command=password_window.destroy)
    cancel_button.grid(pady=10, padx=5, row=0, column=1)

# Icon 
usb_c_64 = "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"

usb_c_decode = base64.b64decode(usb_c_64)
usb_c_byte = Image.open(BytesIO(usb_c_decode))
usb_connect_icon = ctk.CTkImage(light_image=usb_c_byte, size=(32, 32))

usb_d_64 = "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"

usb_d_decode = base64.b64decode(usb_d_64)
usb_d_byte = Image.open(BytesIO(usb_d_decode))
usb_disconnect_icon = ctk.CTkImage(light_image=usb_d_byte, size=(32, 32))

# First window - entry point
def launch_login():
    login_window = ctk.CTkToplevel()
    login_window.title("Login")
    login_window.geometry("300x210")

    def on_login_success():
        login_window.withdraw()
        root.withdraw()
        login_window.after(200, open_app)


    login_frame = ctk.CTkFrame(master=login_window, fg_color="transparent")
    login_frame.pack(pady=20)
    email_label = ctk.CTkLabel(master=login_frame, text="Email : ")
    email_label.grid(pady=5, padx=10, row=0, column=0)
    email_label.configure(text_color="#2E86C1",fg_color="transparent",font=("Arial", 12, "bold"))
    email_entry = ctk.CTkEntry(master=login_frame)
    email_entry.configure(placeholder_text="Enter your email")
    email_entry.grid(pady=5, padx=10, row=0, column=1)
    log_pass_label = ctk.CTkLabel(master=login_frame, text="Password : ")
    log_pass_label.grid(pady=5, padx=10, row=1, column=0)
    log_pass_label.configure(text_color="#2E86C1",fg_color="transparent",font=("Arial", 12, "bold"))
    log_pass_entry = ctk.CTkEntry(master=login_frame, show="*")
    log_pass_entry.grid(pady=5, padx=10, row=1, column=1)
    log_pass_entry.configure(placeholder_text="Enter your password")
    # Checkbox to show/hide password
    show_password = ctk.CTkCheckBox(master=login_window, text="Show Password",checkbox_height= 20,checkbox_width=20 ,command=lambda: log_pass_entry.configure(show="" if show_password.get() else "*"))
    show_password.pack(pady=1)
    login_button = ctk.CTkButton(login_window, text="Login", command=on_login_success)
    login_button.pack(pady=20)



# Second window - main application interface
def open_app():
    main_app = ctk.CTkToplevel()
    main_app.title("USB Security")
    main_app.geometry("600x400")

    def on_main_close():
        main_app.destroy()
        root.destroy()  # Fully exit the app

    main_app.protocol("WM_DELETE_WINDOW", on_main_close)

    title_frame = ctk.CTkFrame(master=main_app, fg_color="transparent", corner_radius=10)
    title_frame.pack(pady=30)

    title = ctk.CTkLabel(master=title_frame,text_color="#2E86C1", text="USB Physical Security", font=("Arial", 20, "bold"))
    title.pack(pady=1)

    pinfo_button = ctk.CTkButton(master=main_app, text="Project Info",hover_color="#d15a15", command=project_info)
    pinfo_button.pack(pady=10)

    usb_status_button = ctk.CTkButton(master=main_app, text="USB Status", hover_color="#d15a15", command=usb_status)
    usb_status_button.pack(pady=10)

    check_log_button = ctk.CTkButton(master=main_app, text="Check Logs", hover_color="#d15a15", command=open_log)
    check_log_button.pack(pady=10)

    usb_frame = ctk.CTkFrame(master=main_app)
    usb_frame.pack(pady=10)

    con_button = ctk.CTkButton(master=usb_frame, image=usb_connect_icon, text="Enable USB", compound="left",
                               fg_color="green", text_color="black", hover_color="#d15a15", command=con_button_clicked)
    con_button.grid(row=0, column=1, pady=10, padx=10)

    discon_button = ctk.CTkButton(master=usb_frame, image=usb_disconnect_icon, text="Disable USB", compound="left",
                                  fg_color="#a31735", text_color="black", hover_color="#d15a15", command=discon_button_clicked)
    discon_button.grid(row=0, column=0, pady=10, padx=10)



# Entry root window

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("350x200")
root.title("USB Security App")

# Title
title_label = ctk.CTkLabel(master=root,text="USB Physical Security",font=ctk.CTkFont("Arial", 28, "bold"),text_color="#2E86C1")
title_label.pack(pady=40)

# Buttons under title
button_frame = ctk.CTkFrame(root, fg_color="transparent")
button_frame.pack()

login_btn = ctk.CTkButton(button_frame, text="Login", width=100, command=launch_login)
login_btn.pack(side="left", padx=20)

register_btn = ctk.CTkButton(button_frame, text="Register", width=100, command=launch_login)
register_btn.pack(side="left", padx=20)

root.mainloop()


