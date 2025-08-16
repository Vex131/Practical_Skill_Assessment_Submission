import threading
import time

import webview
from app import app

def start_flask():
    # Start Flask server
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
 
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    time.sleep(1)

    # Open pywebview window pointing to the Flask app
    webview.create_window("IT Asset Management", "http://127.0.0.1:5000/", maximized=True)
    webview.start()
