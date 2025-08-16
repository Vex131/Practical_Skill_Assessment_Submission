# IT Asset Management Application

This project implements an IT Asset Management system that allows tracking of assets and their assignments to staff members within an organization. It provides functionality to add, edit, and view assets. The system is designed with a MySQL backend and a web interface built with Flask.
## Getting Started

- Ensure your MySQL server is running.
- Ensure the database **asset_management** is created, and Import the included SQL query file to set up the schema.

There are **two ways to run the application**: using Python (source code) or the packaged executable.

### Option 1: Run from Python

1. Make sure you have **Python 3.10+** installed.
2. (Optional) Create and activate a virtual environment in the project folder:
   - Navigate to the project folder **IT_Asset_Management**:
   - Open the command prompt and create a virtual environment:
     ```bash
     python -m venv venv
     
   - Activate the virtual environment:
     ```bash
     venv\Scripts\activate
     
3. Install required packages:
   ```bash
   pip install -r requirements.txt

6. Run the script. 
   ```bash
   python launcher.py
   
### Option 2: Run the Packaged EXE

1. Open the ITAssetManager.exe in the dist folder.

## Notes

1. Both versions require access to the MySQL database with the correct credentials.
2. Both versions come with default MySQL credentials. You may need to update them to match your own database setup in order to run the application.