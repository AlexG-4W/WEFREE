 WEFREE - Portable Secure File Server


  !License (https://img.shields.io/badge/license-MIT-blue.svg)
  !Python (https://img.shields.io/badge/python-3.10%2B-blue.svg)
  !Platform (https://img.shields.io/badge/platform-windows-lightgrey.svg)


  WEFREE is a lightweight, zero-install portable Windows application that turns any folder into a functional web server for remote file access. It’s designed for situations where
  you need to share files across devices (e.g., PC to Phone) instantly without messing with complex network permissions or cloud services.

  ---

  🌟 Key Features
![scr serv](https://github.com/user-attachments/assets/842a4b77-4a9e-49f1-ba30-0284e717ff2f)
![scr1](https://github.com/user-attachments/assets/a8eca84a-6bca-4758-8bf7-b1f0a8f93ca6)


   - Zero-Install Portability: Run as a single .exe file from any directory. No installation required.
   - Desktop GUI Control: A new configuration window allows you to set the password, port, and network binding before launching the server.
   - System Tray Integration: Once started, the server minimizes to the tray, keeping your taskbar clean.
   - Multi-Language Support: Choose between English (Default) and Russian interfaces.
   - Flexible Connectivity (SSL Toggle):
       * HTTPS Mode: Forced encryption for secure transfers.
       * HTTP Mode: Maximum compatibility mode to avoid blocks by aggressive antivirus/firewall software.
   - Full File Management:
       * Browse files and directories.
       * Upload files directly to the server.
       * Download files (optimized for Chrome).
       * Rename and Delete items via the web interface.
   - Secure by Design: Built-in protection against Directory Traversal attacks.

  ---

  🚀 How to Use


   1. Place WEFREE.exe into the folder you want to share.
   2. Run the executable.
   3. In the Settings Window:
       * Set your access password (default: admin123).
       * Select your preferred Language and Connection Mode (HTTP/HTTPS).
       * Note your Local IP displayed in the window.
   4. Click Start Server. The app will minimize to the system tray.
   5. Open your browser on any device in the same network and enter the address provided (e.g., http://192.168.1.15:9999).

  ---

  🛠 Tech Stack


   - Backend: Flask (https://flask.palletsprojects.com/) (Python Web Framework).
   - Frontend: Bootstrap 5 & Bootstrap Icons.
   - GUI: PySide6 (https://doc.qt.io/qtforpython-6/) (Qt for Python).
   - Security: Werkzeug (Password hashing) & pyOpenSSL.
   - Packaging: PyInstaller (https://pyinstaller.org/).

  ---

  🏗 Build from Source

  If you want to modify the code or build the executable yourself:

   1. Requirements: Python 3.10 or higher.
   2. Install dependencies:


   1     pip install -r requirements.txt
   3. Run the build script:
   1     python build.py
   4. Find your portable executable in the dist/ directory.

  ---

  ⚠️ Troubleshooting (Connectivity)


  If you cannot reach the server from your browser:
   1. Check the Port: The default port is 9999. Ensure no other service is using it.
   2. Antivirus/Firewall: Some antivirus software (like Avast or AVG) may block local ports. Try switching to "HTTP (Disable SSL)" in the settings or add WEFREE.exe to your
      antivirus exclusions.
   3. View Logs: Click the "View Server Log" button in the settings window to see real-time server activity.

  ---

  📜 License


  Distributed under the MIT License. See LICENSE for more information.
