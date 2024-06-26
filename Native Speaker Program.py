import os
import webbrowser

from functools import partial
from typing import Dict, Tuple, List
from consolemenu import *
from consolemenu.items import *

import managerCredentials

from objects import Manager, Student, Volunteer, DbHandler, Match, Matcher, MailBox, Human, Email
from utils import check_internet_connection, get_safe_user_input, press_any_key, open_file_with_notepad_and_get_content, clear_screen


YES_NO_QUESTION_OPTIONS = ["y", "Y", "n", "N"]
MANAGER = Manager(managerCredentials.MANAGER_FIRST_NAME,
                      managerCredentials.MANAGER_LAST_NAME,
                      managerCredentials.MANAGER_EMAIL,
                      managerCredentials.MANAGER_API_KEY,
                      managerCredentials.MANAGER_API_SECRET)


def pick_studet() -> Tuple[Student, int]:
    dbHandler = DbHandler()
    students: Dict[int, Student] = dbHandler.db_content["students"]
    index_to_id_map = []

    if not students:
        print("No students in the system...")
        press_any_key()
        return

    for index, (student_id, student) in enumerate(students.items()):
        index_to_id_map.append(student_id)
        print(f"{index}:    {student}")

    student_index = get_safe_user_input("Choose student number: ", input_type=int, expected_inputs=range(len(students)))

    if student_index is None:
        return

    student_id = index_to_id_map[int(student_index)]
    chosen_student = students[student_id]

    return chosen_student, student_id

def pick_volunteer() -> Tuple[Volunteer, int]:
    dbHandler = DbHandler()
    volunteers: Dict[int, Volunteer] = dbHandler.db_content["volunteers"]
    index_to_id_map = []

    if not volunteers:
        print("No volunteers in the system...")
        press_any_key()
        return

    for index, (volunteer_id, volunteer) in enumerate(volunteers.items()):
        index_to_id_map.append(volunteer_id)
        print(f"{index}:    {volunteer}")

    volunteer_index = get_safe_user_input("Choose volunteer number: ", input_type=int, expected_inputs=range(len(volunteers)))

    if volunteer_index is None:
        return

    volunteer_id = index_to_id_map[int(volunteer_index)]
    chosen_volunteer = volunteers[volunteer_id]

    return chosen_volunteer, volunteer_id

def add_student():
    print("Enter Student's details. Press e + enter to exit\n")
    DbHandler().add_object_to_db(Student.interactive())


def add_volunteer():
    print("Enter Volunteer's details. Press e + enter to exit\n")
    DbHandler().add_object_to_db(Volunteer.interactive())


def show_students():
    students = DbHandler().db_content["students"].values()

    for student in students:
        print(student)
    if not len(students):
        print("No existing students")
    else:
        print(f"{len(students)} students")
    press_any_key()


def show_volunteers():
    volunteers = DbHandler().db_content["volunteers"].values()
    
    for volunteer in volunteers:
        print(volunteer)
    if not len(volunteers):
        print("No existing volunteers")
    else:
        print(f"{len(volunteers)} volunteers")
    press_any_key()


def match(match_type: str) -> None:
    if match_type not in ("auto", "manual"):
        return
    
    if match_type == "manual":
        match_action = Matcher(MANAGER).manual_match_and_show
    elif match_type == "auto":
        match_action = Matcher(MANAGER).auto_match_and_show

    if not check_internet_connection():
        print("This action requires internet connection, please connect to the internet and try again")
        press_any_key()
        return

    new_matches = match_action()

    if not new_matches:
        press_any_key()
        return

    approval = get_safe_user_input("\nDo you agree? [y/N]: ", expected_inputs=YES_NO_QUESTION_OPTIONS)
    if approval is None:
        return

    if approval in ("y", "Y"):
        DbHandler().add_objects_to_db(new_matches)
        print("Sending introduction emails to new participants, this might take a while...")
        for match in new_matches:
            match.send_introduction_message()


def show_matches():
    matches = DbHandler().db_content["matches"].values()
    for match in matches:
        print(match)
    if not len(matches):
        print("No existing matches")
    else:
        print(f"\n{len(matches)} matches")
    press_any_key()


def delete_student():
    dbHandler = DbHandler()
    chosen_student, student_id = pick_studet()

    approval = get_safe_user_input(f"\nAre you sure that you want to delete {chosen_student.first_name}? [y/N]: ", expected_inputs=YES_NO_QUESTION_OPTIONS)
    if approval is None:
        return

    if approval in ("y", "Y"):
        related_match_id = dbHandler.get_match_id(student_id=student_id)
        if related_match_id:
            related_match = dbHandler.get_match_by_id(related_match_id)
            related_volunteer = dbHandler.get_volunteer_by_id(related_match.volunteer_id)
            approval = get_safe_user_input(f"{chosen_student.first_name} is matched with {related_volunteer.first_name} {related_volunteer.last_name}\nThis will delete the match. Are you sure? [y/N]: ", expected_inputs=YES_NO_QUESTION_OPTIONS)
            if approval is None:
                return
            if approval in ("y", "Y"):
                dbHandler.delete_match(related_match_id)
            else:
                print("student and match were not deleted")
                press_any_key()
                return
        dbHandler.delete_student(student_id)


def delete_volunteer():
    dbHandler = DbHandler()
    chosen_volunteer, volunteer_id = pick_volunteer()

    approval = get_safe_user_input(f"\nAre you sure that you want to delete {chosen_volunteer.first_name}? [y/N]: ", expected_inputs=YES_NO_QUESTION_OPTIONS)
    if approval is None:
        return

    if approval in ("y", "Y"):
        related_match_id = dbHandler.get_match_id(volunteer_id=volunteer_id)
        if related_match_id:
            related_match = dbHandler.get_match_by_id(related_match_id)
            related_student = dbHandler.get_student_by_id(related_match.student_id)
            approval = get_safe_user_input(f"{chosen_volunteer.first_name} is matched with {related_student.first_name} {related_student.last_name}\nThis will delete the match. Are you sure? [y/N]: ", expected_inputs=YES_NO_QUESTION_OPTIONS)
            if approval in ("y", "Y"):
                dbHandler.delete_match(related_match_id)
            else:
                print("Volunteer and match were not deleted")
                press_any_key()
                return
        dbHandler.delete_volunteer(volunteer_id)


def cancel_match():
    dbHandler = DbHandler()
    matches: Dict[int, Match] = dbHandler.db_content["matches"]
    index_to_id_map = []

    if not matches:
        print("No matches in the system...")
        press_any_key()
        return

    for index, (match_id, match) in enumerate(matches.items()):
        index_to_id_map.append(match_id)
        print(f"{index}:    {match}")

    match_index = get_safe_user_input("Choose match number to cancel: ", input_type=int, expected_inputs=range(len(matches)))
    if match_index is None:
        return

    match_id = index_to_id_map[int(match_index)]
    chosen_match = matches[match_id]

    related_student = dbHandler.get_student_by_id(chosen_match.student_id)
    related_volunteer = dbHandler.get_volunteer_by_id(chosen_match.volunteer_id)

    approval = get_safe_user_input(f"\nAre you sure that you want to cancel the match of {related_student.first_name} and {related_volunteer.first_name}? [y/N]: ", expected_inputs=YES_NO_QUESTION_OPTIONS)
    if approval is None:
        return

    if approval in ("y", "Y"):
        dbHandler.delete_match(match_id)


def remove_matches_and_volunteers():
    approval = get_safe_user_input("Are you sure that you want to delete all matches and students? [y/N]: ", expected_inputs=YES_NO_QUESTION_OPTIONS)
    if approval is None:
        return

    if approval in ("y", "Y"):
        dbHandler = DbHandler()
        dbHandler.delete_all_matches()
        dbHandler.delete_all_students()


def write_and_send_emails(addressees: List[Human]):
    if not check_internet_connection():
        print("This action requires internet connection, please connect to the internet and try again")
        press_any_key()
        return

    clear_screen()
    mail_subject = get_safe_user_input("Enter mail subject: ")
    if not all(chr.isalpha() or chr.isspace() for chr in mail_subject):
        print("Subject not valid. Can contain only alphabetic characters.")
        press_any_key()
        return

    fileName = "tmpMails/" + mail_subject + " - Write your mail here. When you finish, save and close the window"
    mail_content = open_file_with_notepad_and_get_content(fileName)

    approval = get_safe_user_input(f"\nSend the folloing mail?\n\n{mail_subject}\n\n{str(mail_content)}\n\n[Y/n]: ", expected_inputs=YES_NO_QUESTION_OPTIONS)
    if approval is None:
        return
    
    if approval in ("N", "n"):
        press_any_key()
        return

    # make it html format
    mail_content = mail_content.replace("\n", "<br>")
    
    emails = [Email(mail_subject, mail_content, addressee.email) for addressee in addressees]
    MailBox(MANAGER).send_emails(emails)
    print("Sent!")
    press_any_key()


def send_mail_to_student(): write_and_send_emails([pick_studet()[0]])


def send_mail_to_volunteer(): write_and_send_emails([pick_volunteer()[0]])


def send_mail_to_all_students(): write_and_send_emails(list(DbHandler().get_students_from_db().values()))


def send_mail_to_all_volunteers(): write_and_send_emails(list(DbHandler().get_volunteers_from_db().values()))


def open_mailjet_website():
    url = 'https://app.mailjet.com/'

    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
    webbrowser.get(chrome_path).open(url)


def run_menu():
    # Create the menu
    menu = ConsoleMenu("Students & Volunteers Matcher", "Choose an option:")

    # items
    menu.append_item(FunctionItem("Add a Student", add_student))
    menu.append_item(FunctionItem("Add a Volunteer", add_volunteer))
    menu.append_item(FunctionItem("Auto Match", partial(match, "auto")))
    menu.append_item(FunctionItem("Manual Match", partial(match, "manual")))
    menu.append_item(FunctionItem("Show Students", show_students))
    menu.append_item(FunctionItem("Show Volunteers", show_volunteers))
    menu.append_item(FunctionItem("Show Matches", show_matches))
    menu.append_item(FunctionItem("Delete Student", delete_student))
    menu.append_item(FunctionItem("Delete Volunteer", delete_volunteer))
    menu.append_item(FunctionItem("Cancel Match", cancel_match))
    menu.append_item(FunctionItem("Remove Matches and Students (new year)",  remove_matches_and_volunteers))
    menu.append_item(FunctionItem("Send mail to Student", send_mail_to_student))
    menu.append_item(FunctionItem("Send mail to Volunteer", send_mail_to_volunteer))
    menu.append_item(FunctionItem("Send mail to all Students", send_mail_to_all_students))
    menu.append_item(FunctionItem("Send mail to all Volunteers", send_mail_to_all_volunteers))
    menu.append_item(FunctionItem("Open MailJet Website", open_mailjet_website))

    menu.show()


if __name__ == '__main__':
    try:
        run_menu()
    except KeyboardInterrupt:
        press_any_key()
