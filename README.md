# 🔍 Port Scanner GUI

A simple and interactive port scanner application built with **Python** and **Kivy**. This tool allows users to scan a target host for open TCP ports and displays services and banners, if available.

## 🚀 Features

- Scan common or custom port ranges on any host
- View open ports with associated service names and banners
- Simple, responsive GUI using Kivy
- Clear feedback and progress display during scan

## 🖼️ GUI Preview
#### This is the application interface in macOS.
<img width="792" alt="image" src="https://github.com/user-attachments/assets/a7926c97-de23-49d3-bc86-b26796c7aff3" />

#### The Scan Results with open ports and services. 
<img width="789" alt="image" src="https://github.com/user-attachments/assets/62a067f4-a94b-4648-88cb-6d5bae387866" />

## 🧠 How It Works
- Accepts a hostname or IP address input
- Scans common ports or a specified range
- Uses Python’s socket module for TCP connection attempts
- Displays results in a formatted output


## 📦 Requirements

- Python 3.7+
- [Kivy](https://kivy.org/doc/stable/)

### Install dependencies using:

```bash
pip install -r requirements.txt
```

## 🔧 Installation
### Windows/macOS (Standalone App)
1. Download the latest `.exe` (Windows) or `.app` (macOS) from the [Releases](https://github.com/aniket-cs/YellowTag/tree/master/Releases/) section.
2. Run the application without needing Python.

### Run from Source Code (Python 3 Required)
1. Clone the repository:
   ```bash
   git clone https://github.com/aniket-cs/YellowTag.git
   cd YellowTag
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python port_scanner.py
   ```

## Building the Application
### **Windows/macOS: Generate Executable (.exe/.app)**
```bash
pyinstaller --onefile --windowed port_scanner.py
```
OR, if you don't want to add any image / icon / logo to your app :
```bash
pyinstaller --onefile --windowed port_scanner.py
```
### **Android: Generate APK**
```bash
buildozer -v android debug
```
For a signed APK:
```bash
buildozer android release
```

## License
This project is open-source. I welcome all engineers to contribute and make the application cool :)


## 👤 Author
**Aniket Das**
[GitHub](https://github.com/aniket-cs/)


------
⭐ **Star this repo** if you found it useful!
