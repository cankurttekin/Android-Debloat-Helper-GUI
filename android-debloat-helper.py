import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog, font, ttk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Debloat Helper")

        # Define fonts
        self.large_font = font.Font(size=14, weight='bold')
        self.medium_font = font.Font(size=14)
        
        # Define colors
        self.primary_color = '#1c71d8'
        self.secondary_color = '#e01b24'
        self.restore_color = "#dcdcdc"
        
        # Set the initial window size
        self.root.geometry("600x800")
        self.root.configure(bg='white')

        # Device info label
        self.device_info_label = tk.Label(root, text="No device connected", font=self.large_font, bg='white')
        self.device_info_label.pack(pady=10)

        # Connect button
        self.connect_button = tk.Button(root, text="Connect", command=self.connect_device, font=self.medium_font, bg=self.primary_color, fg='white')
        self.connect_button.pack(pady=10)

        # Refresh apps button
        self.refresh_button = tk.Button(root, text="Refresh Apps", command=self.refresh_apps, font=self.medium_font, bg=self.primary_color, fg='white', state=tk.DISABLED)
        self.refresh_button.pack(pady=10)

        # Search bar
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(root, textvariable=self.search_var, font=self.medium_font)
        self.search_entry.pack(pady=10)
        self.search_var.trace('w', self.filter_list)

        # Listbox
        self.listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, font=self.medium_font, bg='white')
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Uninstall button
        self.uninstall_button = tk.Button(root, text="Uninstall", command=self.uninstall_app, font=self.medium_font, bg=self.secondary_color, fg='white', state=tk.DISABLED)
        self.uninstall_button.pack(pady=10)

        # Restore button
        self.restore_button = tk.Button(root, text="Restore", command=self.restore_app, font=self.medium_font, bg=self.restore_color, fg='black', state=tk.DISABLED)
        self.restore_button.pack(pady=10)

        # Initialize variables
        self.selected_device = None
        self.selected_packages = set()  # Use a set to store selected package names

    def connect_device(self):
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            device_lines = result.stdout.splitlines()
            devices = [line.split('\t')[0] for line in device_lines[1:] if line.strip()]

            if devices:
                if len(devices) == 1:
                    self.use_device(devices[0])
                else:
                    self.select_device(devices)
            else:
                self.device_info_label.config(text="No device connected")
                messagebox.showerror("Connection", "No device found. Make sure USB debugging is enabled.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while connecting to device: {str(e)}")

    def use_device(self, device):
        try:
            manufacturer_result = subprocess.run(["adb", "-s", device, "shell", "getprop", "ro.product.manufacturer"], capture_output=True, text=True)
            model_result = subprocess.run(["adb", "-s", device, "shell", "getprop", "ro.product.model"], capture_output=True, text=True)
            
            manufacturer = manufacturer_result.stdout.strip()
            model = model_result.stdout.strip()

            self.device_info_label.config(text=f"Connected Device: {manufacturer} {model}")
            messagebox.showinfo("Connection", f"Device connected successfully!\nManufacturer: {manufacturer}\nModel: {model}")

            # Save selected device ID for future operations
            self.selected_device = device

            # Enable buttons after successful connection
            self.refresh_button.config(state=tk.NORMAL)
            self.uninstall_button.config(state=tk.NORMAL)
            self.restore_button.config(state=tk.NORMAL)

            # Refresh apps list after connection
            self.refresh_apps()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while using the device: {str(e)}")

    def select_device(self, devices):
        device_selection = tk.Toplevel(self.root)
        device_selection.title("Select Device")
        
        tk.Label(device_selection, text="Select a device to connect:", font=self.large_font).pack(pady=10)
        
        selected_device = tk.StringVar()
        
        for device in devices:
            try:
                manufacturer_result = subprocess.run(["adb", "-s", device, "shell", "getprop", "ro.product.manufacturer"], capture_output=True, text=True)
                model_result = subprocess.run(["adb", "-s", device, "shell", "getprop", "ro.product.model"], capture_output=True, text=True)
                
                manufacturer = manufacturer_result.stdout.strip()
                model = model_result.stdout.strip()

                # Display ADB device name along with manufacturer and model
                device_label = f"{device} - {manufacturer} {model}"
                tk.Radiobutton(device_selection, text=device_label, variable=selected_device, value=device, font=self.large_font).pack(anchor=tk.W)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while fetching device info: {str(e)}")

        def on_select():
            if selected_device.get():
                self.use_device(selected_device.get())
                device_selection.destroy()
            else:
                messagebox.showerror("Error", "No device selected")

        tk.Button(device_selection, text="Connect", command=on_select, font=self.large_font).pack(pady=10)

    def refresh_apps(self):
        self.listbox.delete(0, tk.END)
        try:
            result = subprocess.run(["adb", "-s", self.selected_device, "shell", "pm", "list", "packages", "--user", "0"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                packages = result.stdout.splitlines()
                for pkg in packages:
                    self.listbox.insert(tk.END, pkg.replace("package:", ""))
                    
                # Re-select previously selected items
                for idx, item in enumerate(self.listbox.get(0, tk.END)):
                    if item in self.selected_packages:
                        self.listbox.selection_set(idx)
            else:
                messagebox.showerror("Error", f"Failed to retrieve package list:\n{result.stderr}")
        except subprocess.TimeoutExpired:
            messagebox.showerror("Timeout", "Connection timed out. Please check your device and try again.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Command execution failed: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def uninstall_app(self):
        selected_apps = list(self.selected_packages)
        if not selected_apps:
            messagebox.showerror("Error", "No package selected for uninstallation.")
            return
        
        app_list = "\n".join(selected_apps)
        confirmation = messagebox.askyesno("Confirm Uninstall", f"The following packages will be uninstalled:\n\n{app_list}\n\nDo you want to proceed?")
        if confirmation:
            for app in selected_apps:
                try:
                    subprocess.run(["adb", "-s", self.selected_device, "shell", "pm", "uninstall", "-k", "--user", "0", app], check=True)
                    print(f"Uninstalled package: {app}")  # Log to console
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Failed to uninstall {app}: {str(e)}")
            messagebox.showinfo("Uninstall", "Selected packages have been uninstalled.")
            self.refresh_apps()

    def restore_app(self):
        package_name = simpledialog.askstring("Restore App", "Enter package name to restore:")
        if package_name:
            try:
                subprocess.run(["adb", "-s", self.selected_device, "shell", "cmd", "package", "install-existing", package_name], check=True)
                messagebox.showinfo("Restore", f"Restored {package_name}")
                self.refresh_apps()
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to restore {package_name}: {str(e)}")

    def filter_list(self, *args):
        search_term = self.search_var.get().strip().lower()
        all_items = [self.listbox.get(idx) for idx in range(self.listbox.size())]
        
        self.listbox.delete(0, tk.END)
        
        for item in all_items:
            if search_term == "" or search_term in item.lower():
                self.listbox.insert(tk.END, item)
                if item in self.selected_packages:
                    self.listbox.selection_set(tk.END)

    def on_select(self, event):
        selected_items = [self.listbox.get(idx) for idx in self.listbox.curselection()]
        self.selected_packages.clear()
        self.selected_packages.update(selected_items)

# Create and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.listbox.bind('<<ListboxSelect>>', app.on_select)
    root.mainloop()

