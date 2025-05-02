from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.modalview import ModalView
from threading import Thread
import socket
import concurrent.futures
import os
import pyperclip
import json
from datetime import datetime

# Set window background to dark
Window.clearcolor = (0.05, 0.05, 0.05, 1)

class StyledTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.2, 0.2, 1)
        self.foreground_color = (1, 1, 0, 1)
        self.cursor_color = (1, 1, 0, 1)
        self.padding = [10, 10, 10, 10]
        self.font_size = 20

class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (1, 1, 0, 1)
        self.color = (0, 0, 0, 1)
        self.bold = True
        self.font_size = 24
        self.size_hint = (1, None)
        self.height = 55
        self.background_normal = ''
        self.background_down = ''

class YellowTagLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=120, spacing=20, **kwargs)

        self.add_widget(Label(text='YellowTag - Port Scanner', font_size=40, bold=True, color=(1, 1, 0, 1), size_hint=(1, None), height=150))

        self.add_widget(Label(text='Target IP', font_size=30, color=(1, 1, 0, 1), size_hint=(1, None), height=30))
        self.input_ip = StyledTextInput(hint_text='e.g. 192.168.0.1', multiline=False, size_hint=(1, None), height=40)
        self.add_widget(self.input_ip)

        self.add_widget(Label(text='Start Port', font_size=30, color=(1, 1, 0, 1), size_hint=(1, None), height=30))
        self.input_start_port = StyledTextInput(hint_text='e.g. 20', multiline=False, input_filter='int', size_hint=(1, None), height=40)
        self.add_widget(self.input_start_port)

        self.add_widget(Label(text='End Port', font_size=30, color=(1, 1, 0, 1), size_hint=(1, None), height=30))
        self.input_end_port = StyledTextInput(hint_text='e.g. 100', multiline=False, input_filter='int', size_hint=(1, None), height=40)
        self.add_widget(self.input_end_port)

        self.scan_button = StyledButton(text='Start Scan')
        self.scan_button.bind(on_press=self.start_scan)
        self.add_widget(self.scan_button)

        self.progress = ProgressBar(max=100, value=0, size_hint=(1, None), height=20)
        self.add_widget(self.progress)

        self.progress_label = Label(text='', font_size=25, color=(1, 1, 0, 1), size_hint=(1, None), height=25)
        self.add_widget(self.progress_label)

        self.results = Label(text='Scan results will appear here.', size_hint_y=None, valign='top', halign='left', color=(1, 1, 0, 1))
        self.results.bind(texture_size=self.results.setter('size'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.results)
        self.add_widget(scroll)

        button_row = BoxLayout(size_hint=(1, None), height=55, spacing=10)
        self.export_button = StyledButton(text='Export Results')
        self.copy_button = StyledButton(text='Copy All')
        self.json_button = StyledButton(text='Export JSON')
        self.export_button.bind(on_press=self.export_results)
        self.copy_button.bind(on_press=self.copy_all_results)
        self.json_button.bind(on_press=self.export_json_results)
        button_row.add_widget(self.export_button)
        button_row.add_widget(self.copy_button)
        button_row.add_widget(self.json_button)
        self.add_widget(button_row)

    def start_scan(self, instance):
        target_host = self.input_ip.text.strip()
        try:
            start_port = int(self.input_start_port.text.strip())
            end_port = int(self.input_end_port.text.strip())
        except ValueError:
            self.show_popup("Invalid Port", "Please enter valid start and end ports.")
            return

        if not target_host:
            self.show_popup("Missing IP", "Please enter a valid IP address.")
            return

        self.results.text = ""
        self.progress.value = 0
        self.progress_label.text = "Starting scan...."
        Thread(target=self.run_scan, args=(target_host, start_port, end_port), daemon=True).start()

    def run_scan(self, target_host, start_port, end_port):
        try:
            target_ip = socket.gethostbyname(target_host)
        except socket.gaierror:
            self.results.text = "Invalid hostname or IP."
            return

        total_ports = end_port - start_port + 1
        results = []
        self.scanned_ports = 0

        def update_progress(dt):
            progress_value = (self.scanned_ports / total_ports) * 100
            self.progress.value = progress_value
            self.progress_label.text = f"Scanned {self.scanned_ports} of {total_ports} ports ({int(progress_value)}%)"

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(self.scan_port, target_ip, port): port for port in range(start_port, end_port + 1)}
            for future in concurrent.futures.as_completed(futures):
                port, service, banner, status = future.result()
                results.append((port, service, banner, status))
                self.scanned_ports += 1
                Clock.schedule_once(update_progress)

        self.progress_label.text = "Scan complete."
        self.scan_results_data = results
        formatted = self.format_port_results(results)
        self.results.text = formatted

    def scan_port(self, target_ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                try:
                    service = socket.getservbyport(port, 'tcp')
                except:
                    service = 'Unknown'
                banner = self.get_banner(sock)
                return port, service, banner, True
            else:
                return port, '', '', False
        except:
            return port, '', '', False
        finally:
            sock.close()

    def get_banner(self, sock):
        try:
            sock.settimeout(1)
            return sock.recv(1024).decode(errors='ignore').strip()
        except:
            return ''

    def format_port_results(self, results):
        output = ""
        open_ports_found = False  # Flag to check if any open ports exist

        for port, service, banner, status in results:
            if status:
                if not open_ports_found:
                    # Add header only once, when first open port is found
                    output += "Port    Service        Status\n"
                    output += "-" * 40 + "\n"
                    open_ports_found = True
                output += f"{port:<8}{service:<15}Open\n"
                if banner:
                    banner_lines = banner.split('\n')
                    for line in banner_lines:
                        output += f"{'':<8}{line}\n"

        if not open_ports_found:
            output += "No open ports found.\n"

        return output

    def export_json_results(self, instance):
        if not hasattr(self, 'scan_results_data') or not self.scan_results_data:
            self.show_popup("No Data", "There are no scan results to export.")
            return

        json_data = [
            {
                "port": port,
                "service": service,
                "banner": banner,
                "status": "open" if status else "closed"
            }
            for port, service, banner, status in self.scan_results_data
            if status or not self.open_ports_only.active
        ]

        filename = f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)

        self.show_popup("Export Successful", f"Results saved to:\n{filename}")

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        close_button = StyledButton(text='Close')
        content.add_widget(close_button)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def export_results(self, instance):
        if not self.results.text.strip():
            self.show_popup("No Data", "There are no scan results to export.")
            return

        filechooser = FileChooserIconView(path=os.getcwd(), size_hint=(1, 1))
        save_button = StyledButton(text="Save")
        cancel_button = StyledButton(text="Cancel")

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(filechooser)
        layout.add_widget(save_button)
        layout.add_widget(cancel_button)

        popup = ModalView(size_hint=(0.9, 0.9))
        popup.add_widget(layout)

        def save_file(instance):
            path = filechooser.path
            filename = filechooser.selection[0] if filechooser.selection else os.path.join(path, "scan_results.txt")
            if not filename.lower().endswith((".txt", ".csv")):
                filename += ".txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.results.text)
            popup.dismiss()
            self.show_popup("Export Successful", f"Results saved to:\n{filename}")

        save_button.bind(on_press=save_file)
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def copy_all_results(self, instance):
        if self.results.text.strip():
            pyperclip.copy(self.results.text)
            self.show_popup("Copied", "Scan results copied to clipboard.")
        else:
            self.show_popup("No Data", "There are no scan results to copy.")

class YellowTagApp(App):
    def build(self):
        return YellowTagLayout()

if __name__ == '__main__':
    YellowTagApp().run()
