import PyInstaller.__main__
import os
import shutil

def build():
    # Define the application name
    app_name = "WEFREE"
    
    # Arguments for PyInstaller
    args = [
        'app.py',
        '--name=%s' % app_name,
        '--onefile',         # Create a single executable
        '--console',         # Show console for logs
        '--clean',           # Clean cache
        '--collect-all=flask',
        '--collect-all=werkzeug',
        '--collect-all=cryptography',
    ]
    
    print("Starting build process...")
    PyInstaller.__main__.run(args)
    
    print("\nBuild complete!")
    print(f"Your portable executable is in the 'dist' folder: dist/{app_name}.exe")

if __name__ == "__main__":
    build()
