# Students and Volunteers: Native Speakers Program

> My dad is a professor of English education at several colleges in Israel. Years ago, he initiated the NativeSpeakersProgram to pair his students with native English speakers. However, managing the logistics manually was incredibly challenging. Tasks like volunteer retention, student matching, and sending reminders consumed a significant amount of his energy. I developed this project to make his life easier. Since its launch, managing the program has become effortless for him. He continues to use the system year after year, and to this day, he keeps asking me to add new features!

An open-source desktop application that connects students with English-speaking volunteers to improve students' oral English proficiency. The application automates the matching process, handles communications via Mailjet, and schedules periodic reminders to check on match satisfaction.

## Features

- **Modern GUI**: Built using customtkinter and CTkTable for a clean, sleek user interface.
- **Dynamic Dashboards**: Separate views for Students, Volunteers, and Matches.
- **Matching System**:
  - **Auto Match**: Automatically suggests appropriate matches based on preference constraints (e.g., gender preferences).
  - **Manual Match**: Hand-pick student-volunteer pairs.
- **Automated Communication**: Sends introduction emails to newly-paired students and volunteers via the Mailjet API.
- **Reminders**: Send custom group or individual emails directly from the GUI.
- **Background Reminder Script**: Run reminder_sender.py periodically (via a task scheduler/cron job) to check matches and automatically send follow-up emails after a set number of days.
- **Local JSON Database**: Keeps all records locally in a readable JSON format (db.json).

---

## Requirements

- **Python**: version 3.8 or higher.
- **Dependencies**: Listed in requirements.txt.

---

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Chaiky3/StudentsAndVolunteers.git
   cd StudentsAndVolunteers
   ```

2. **Install Dependencies**:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Configure API Credentials**:
   - Locate `managerCredentials_template.py` in the root directory.
   - Copy or rename it to `managerCredentials.py`:
     ```bash
     cp managerCredentials_template.py managerCredentials.py
     ```
   - Open `managerCredentials.py` and replace the placeholder values with your Mailjet API keys and manager details:
     ```python
     MANAGER_FIRST_NAME = "YourFirstName"
     MANAGER_LAST_NAME = "YourLastName"
     MANAGER_EMAIL = "your.email@example.com"
     MANAGER_API_KEY = "your_mailjet_api_key"
     MANAGER_API_SECRET = "your_mailjet_api_secret"
     ```
   *(Note: `managerCredentials.py` is ignored by Git to secure your secrets).*

---

## How to Run

### 1. Launch the Desktop Application
Run the graphical program to manage students, volunteers, and match pairs:
```bash
python "Native Speaker Program.py"
```

### 2. Run the Reminder Script
To automate sending follow-up reminders, schedule the following script to run once daily (e.g., using Windows Task Scheduler or Cron on Linux):
```bash
python reminder_sender.py
```
This script evaluates matches, monitors the days elapsed since matching, and sends reminders if a set threshold is reached (configured in consts.py).

---

## Project Structure

- `Native Speaker Program.py` — The main GUI desktop application entry point.
- `objects.py` — Contains data classes (Student, Volunteer, Match, Manager, Email, MailBox) and database handler code.
- `consts.py` — Application configuration constants, timing thresholds, and HTML email templates.
- `utils.py` — Helper functions for I/O operations, network connectivity checks, and other utilities.
- `reminder_sender.py` — Automated script that checks matches and sends follow-up reminder emails.
- `managerCredentials_template.py` — Template file for credentials setup.
- `requirements.txt` — List of third-party package dependencies.
- `LICENSE` — The official MIT license for open-source distribution.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
