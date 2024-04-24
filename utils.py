import os
import time
import urllib.request
import urllib.error

from typing import Optional, List, Any


EXIT_CODE = 'e'
INVALID_INPUT = "Invalid input"


def press_any_key():
    input("\nPress Enter to continue...")


def check_internet_connection() -> bool:
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except urllib.error.URLError:
        return False


def wait_for_internet_connection():
    while True:
        if check_internet_connection():
            print("Connected to internet")
            return
        print("Waiting for internet connection")
        time.sleep(5)


def get_safe_user_input(text: str, input_type: type = str, expected_inputs: Optional[List[Any]] = None) -> Any:
    user_input = input(text)
    if user_input == EXIT_CODE:
        return None
    try:
        user_input = input_type(user_input)
        if not expected_inputs:
            return user_input
        if user_input not in expected_inputs:
            print(INVALID_INPUT)
            time.sleep(2)
            return None
        return user_input

    except TypeError:
        print(INVALID_INPUT)
        time.sleep(2)
        return None


def open_file_with_notepad_and_get_content(fileName) -> str:
    mail_content = ""
    with open(fileName, 'w') as f:
        pass

    # open file with notepad
    os.system(f"notepad.exe {fileName}")
    
    # get file content
    with open(fileName, 'r') as f:
        mail_content = f.read()

    # delete tmp file
    os.remove(fileName)

    return mail_content

def clear_screen():
    os.system("cls")