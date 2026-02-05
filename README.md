WEFREE - Portable Secure File Server

**WEFREE** is a lightweight, portable Windows application that turns any folder into a secure, encrypted web server for remote file access. 

## Key Features
- **Portable**: Run it from any folder as a single `.exe` file without installation.
- **Secure**: Forced HTTPS/SSL encryption for all data transfers.
- **Protected**: Mandatory password authentication to access your files.
- **File Management**: 
    - Browse files and directories.
    - Download files.
    - Upload files directly to the server.
- **Safe**: Built-in protection against Directory Traversal attacks.

## How to Use
1.  Place `WEFREE.exe` into the folder you want to share.
2.  Run `WEFREE.exe`.
3.  On the first run, it will automatically:
    - Create a `config.json` file.
    - Generate self-signed SSL certificates in the `certs/` folder.
    - Start the server on port `5000` with the default password: `admin123`.

## Accessing the Server
- Open your browser and go to: `https://localhost:5000` (or use your computer's local IP address).
- **Security Warning**: Since the app uses a self-signed certificate, your browser will show a "Your connection is not private" warning. 
    - Click **Advanced** -> **Proceed to localhost (unsafe)**.
- Log in using the password from `config.json` (Default: `admin123`).

## Configuration
Open `config.json` to customize the following settings:
- `password_hash`: Securely stored password.
- `port`: The port the server runs on (Default: 5000).
- `allow_uploads`: Set to `true` or `false`.

## Remote Access (Over the Internet)
To access your files from outside your local network:
1.  **Port Forwarding**: Configure your router to forward port `5000` to your computer's local IP.
2.  **Tunneling Services**: Use tools like [ngrok](https://ngrok.com/) or [Tailscale](https://tailscale.com/) if you don't have access to router settings.

## Build from Source
If you want to build the executable yourself:
1.  Install Python 3.10+.
2.  Install dependencies: `pip install -r requirements.txt`.
3.  Install PyInstaller: `pip install pyinstaller`.
4.  Run the build script: `python build.py`.
5.  Find your app in the `dist/` directory.

## License
Distributed under the MIT License. See `LICENSE` for more information.
