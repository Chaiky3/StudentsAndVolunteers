import webbrowser

from typing import Dict
from consolemenu import *
from consolemenu.items import *

import managerCredentials

from objects import Manager, Student, Volunteer, DbHandler, Match, Matcher
from utils import check_internet_connection, get_safe_user_input


YES_NO_QUESTION_OPTIONS = ["y", "Y", "n", "N"]


def press_any_key():
    input("\nPress Enter to continue...")


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


def auto_match():
    if not check_internet_connection():
        print("This action requires internet connection, please connect to the internet and try again")
        press_any_key()
        return
    manager = Manager(managerCredentials.MANAGER_FIRST_NAME,
                      managerCredentials.MANAGER_LAST_NAME,
                      managerCredentials.MANAGER_EMAIL,
                      managerCredentials.MANAGER_API_KEY,
                      managerCredentials.MANAGER_API_SECRET)
    new_matches = Matcher(manager).match_and_show()
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


def manual_match():
    print("This option is currently not supported...\n")
    press_any_key()


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
    students: Dict[int, Student] = dbHandler.db_content["students"]
    index_to_id_map = []

    if not students:
        print("No students in the system...")
        press_any_key()
        return

    for index, (student_id, student) in enumerate(students.items()):
        index_to_id_map.append(student_id)
        print(f"{index}:    {student}")

    student_index = get_safe_user_input("Choose student number to delete: ", input_type=int, expected_inputs=range(len(students)))

    if student_index is None:
        return

    student_id = index_to_id_map[int(student_index)]
    chosen_student = students[student_id]

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
    volunteers: Dict[int, Volunteer] = dbHandler.db_content["volunteers"]
    index_to_id_map = []

    if not volunteers:
        print("No volunteers in the system...")
        press_any_key()
        return

    for index, (volunteer_id, volunteer) in enumerate(volunteers.items()):
        index_to_id_map.append(volunteer_id)
        print(f"{index}:    {volunteer}")

    volunteer_index = get_safe_user_input("Choose volunteer number to delete: ", input_type=int, expected_inputs=range(len(volunteers)))
    if volunteer_index is None:
        return

    volunteer_id = index_to_id_map[int(volunteer_index)]
    chosen_volunteer = volunteers[volunteer_id]

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
    menu.append_item(FunctionItem("Auto Match", auto_match))
    menu.append_item(FunctionItem("Manual Match", manual_match))
    menu.append_item(FunctionItem("Show Students", show_students))
    menu.append_item(FunctionItem("Show Volunteers", show_volunteers))
    menu.append_item(FunctionItem("Show Matches", show_matches))
    menu.append_item(FunctionItem("Delete Student", delete_student))
    menu.append_item(FunctionItem("Delete Volunteer", delete_volunteer))
    menu.append_item(FunctionItem("Cancel Match", cancel_match))
    menu.append_item(FunctionItem("Remove Matches and Students (new year)",  remove_matches_and_volunteers))
    menu.append_item(FunctionItem("Open MailJet Website", open_mailjet_website))

    menu.show()


if __name__ == '__main__':
    run_menu()
