# 📂 Python Download Notifier

A robust desktop application for real-time monitoring of specific folders. Built with **Python** and **PyQt6**, it runs in the system tray to track new files and sends native Windows desktop notifications.

## 🚀 Key Features

- **Real-Time Monitoring:** Watches selected folders for new files using the `watchdog` library.
- **Smart Filtering:** Ignores temporary files (`.tmp`, `.crdownload`, `.part`) to avoid false alerts during downloads.
- **Desktop Notifications:** Shows native Windows toast notifications when a download completes.
- **System Tray Integration:** Runs silently in the background. Minimizes to tray instead of closing.
- **Persistent Configuration:** Automatically saves monitored folder paths to `config.json`.
- **Clean GUI:** Modern dark interface built with PyQt6.

## 📸 Screenshots

### Main Interface & Monitoring
<img width="1365" height="722" alt="4" src="https://github.com/user-attachments/assets/88ccfb8a-1375-4fb7-bc51-ab04f36072fa" />
<img width="1365" height="716" alt="1" src="https://github.com/user-attachments/assets/d51d28c0-3482-4088-9a45-6be1fa335ee0" />

### Desktop Notification
<img width="1365" height="714" alt="3" src="https://github.com/user-attachments/assets/f80d689d-011c-4f5a-9567-9dbe68294e18" />


### System Tray Operation

<img width="368" height="113" alt="5" src="https://github.com/user-attachments/assets/3a79a8c5-4037-468d-aa00-3c4b7011bd7e" />

> *The application continues running even when the main window is closed.*

## 🛠️ Technologies Used

- **Language:** Python 3.x
- **GUI Framework:** PyQt6
- **File Monitoring:** watchdog
- **Notifications:** plyer + Windows native API
- **Threading:** QtCore.QThread (non-blocking background tasks)
- **Configuration:** JSON

## ⚙️ Installation & Usage

### Prerequisites
- Python 3.8 or higher
- Windows 10/11

### Steps

1.  Clone the repository:
    ```bash
    git clone https://github.com/sergiomoscoso/python-download-notifier.git
    cd python-download-notifier
    ```

2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Run the application:
    ```bash
    python main.py
    ```

5.  Click **"Añadir carpeta"**, select your download folder, and click **"Iniciar monitoreo"**.

## 📁 Project Structure
