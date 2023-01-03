from consolemenu import *
from consolemenu.items import *

import consts, managerCredentials
from objects import Manager, Student, Volunteer, DbHandler, Matcher, check_internet_connection


def press_any_key():
    input("\nPress any key to continue...")

def add_student():
    print("Enter Student's details. Press e + enter to exit\n")
    DbHandler().add_object_to_db(Student.interactive())

def add_volunteer():
    print("Enter Volunteer's details. Press e + enter to exit\n")
    DbHandler().add_object_to_db(Volunteer.interactive())

def show_students():
    students = DbHandler().db_content["students"]
    for student in students:
        print(student)
    if len(students) == 0:
        print("No existing students")
    press_any_key()

def show_volunteers():
    volunteers = DbHandler().db_content["volunteers"]
    for volunteer in volunteers:
        print(volunteer)
    if len(volunteers) == 0:
        print("No existing volunteers")
    press_any_key()

def auto_match():
    if not check_internet_connection():
        print("This action requires internet connection, please connect to the internet and try again")
        press_any_key()
        return
    manager = Manager(consts.DEFAULT_MANAGER_FIRST_NAME,
                      consts.DEFAULT_MANAGER_LAST_NAME,
                      managerCredentials.DEFAULT_MANAGER_EMAIL,
                      managerCredentials.DEFAULT_MANAGER_PASSWORD)
    matches = Matcher(manager).match_and_show()
    approval = input("\nDo you agree? [y/N]: ")
    if approval in ("y", "Y"):
        DbHandler().add_objects_to_db(matches)
        print("Sending introduction emails to new participants, this might take a while...")
        for match in matches:
            match.send_introduction_message()


def manual_match():
    print("This option is currently not supported...\n")
    press_any_key()

def show_matches():
    matches = DbHandler().db_content["matches"]
    for match in matches:
        print(match)
    if len(matches) == 0:
        print("No existing matches")
    input("\nEnter any key to continue...")

# def delete_student():
#     dbHandler = DbHandler()
#     students: list = DbHandler().db_content["students"]
#     for index, student in enumerate(students):
#         print(f"{index}:    {student}")
    
#     student_index = int(input("Choose student number to delete: "))
#     approval = input(f"\nAre you sure that you want to delete {students[student_index].first_name}? [y/N]: ")
#     if approval in ("y", "Y"):
#         dbHandler.delete_student(students[student_index])

# def delete_volunteer():
#     dbHandler = DbHandler()
#     volunteers: list = DbHandler().db_content["volunteers"]
#     for index, volunteer in enumerate(volunteers):
#         print(f"{index}:    {volunteer}")

#     volunteer_index = int(input("Choose volunteer number to delete: "))
#     approval = input(f"\nAre you sure that you want to delete {volunteers[volunteer_index].first_name}? [y/N]: ")
#     if approval in ("y", "Y"):
#         dbHandler.delete_volunteer(volunteers[volunteer_index])

# def cancel_match():
#     dbHandler = DbHandler()
#     matches: list = DbHandler().db_content["matches"]
#     for index, match in enumerate(matches):
#         print(f"{index}:    {match}")

#     match_index = int(input("Choose match number to delete: "))
#     approval = input(f"\nAre you sure? Cancelation emails will be sent to {match.student.first_name} and {match.volunteer.first_name} [y/N]: ")
#     if approval in ("y", "Y"):
#         match.send_cancelation_messages()
#         dbHandler.delete_match(matches[match_index])

def remove_matches_and_volunteers():
    approval = input("Are you sure that you want to delete all matches and students? [y/N]: ")
    if approval in ("y", "Y"):
        dbHandler = DbHandler()
        dbHandler.delete_all_matches()
        dbHandler.delete_all_students()

def run_menu():
    # Create the menu
    menu = ConsoleMenu("Students & Volunteers Matcher", "Choose an option:")

    # items
    menu.append_item(FunctionItem("Add a student", add_student))
    menu.append_item(FunctionItem("Add a volunteer", add_volunteer))
    menu.append_item(FunctionItem("Auto Match", auto_match))
    menu.append_item(FunctionItem("Manual Match", manual_match))
    menu.append_item(FunctionItem("Show students", show_students))
    menu.append_item(FunctionItem("Show volunteers", show_volunteers))
    menu.append_item(FunctionItem("Show Matches", show_matches))
    # menu.append_item(FunctionItem("Delete student", delete_student))
    # menu.append_item(FunctionItem("Delete student", delete_volunteer))
    # menu.append_item(FunctionItem("Cancel match", cancel_match))
    menu.append_item(FunctionItem("Remove Matches and Students (new year)",  remove_matches_and_volunteers))

    menu.show()


if __name__ == '__main__':
    run_menu()