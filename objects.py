from __future__ import annotations

import ssl
import json
import smtplib
import urllib.request
import urllib.error

from time import sleep
from datetime import datetime
from contextlib import suppress
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

import consts


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
        sleep(5)

@dataclass_json
@dataclass(eq=True)
class Writeable():
    pass

@dataclass(eq=True)
class Human(Writeable):
    first_name: str
    last_name: str
    email: str = field(compare=False)

    def __repr__(self) -> str:
        return f"""
        name: {self.first_name} {self.last_name}
        email: {self.email}
        """

@dataclass(eq=True)
class Student(Human):
    def __repr__(self) -> str:
        return super().__repr__()

    @staticmethod
    def interactive() -> Student:
        params = []
        for attr in ("First Name", "Last Name", "Email"):
            user_input = input(f"Enter {attr}: ")
            if user_input == "e":
                return
            params.append(user_input)
        
        return Student(*params)

@dataclass(eq=True)
class Volunteer(Human):
    phone: str = field(compare=False)

    def __repr__(self) -> str:
        return super().__repr__() + f"""phone: {self.phone}
        """

    @staticmethod
    def interactive() -> Volunteer:
        params = []
        for attr in ("First Name", "Last Name", "Email", "Phone Number"):
            user_input = input(f"Enter {attr}: ")
            if user_input == "e":
                return
            params.append(user_input)
        
        return Volunteer(*params)

@dataclass(eq=True)
class Manager(Human):
    password: str

@dataclass(eq=True)
class Match(Writeable):
    manager: Manager
    student: Student
    volunteer: Volunteer
    date: Tuple[int, int] = field(default=(datetime.now().year, datetime.now().month, datetime.now().day), compare=False)
    first_reminder_sent: bool = field(default=False, compare=False)
    second_reminder_sent: bool = field(default=False, compare=False)

    def __repr__(self) -> str:
        return f"{self.student.first_name} {self.student.last_name} <--> {self.volunteer.first_name} {self.volunteer.last_name}"

    def send_introduction_message(self) -> None:
        subject = "Introduction to native speakers program"

        message_for_student = consts.STUDENT_INTRODUCTION_STR.format(self.student.first_name,
                                                                                 self.volunteer.first_name,
                                                                                 self.volunteer.last_name,
                                                                                 self.volunteer.phone,
                                                                                 self.volunteer.email,
                                                                                 self.manager.first_name,
                                                                                 self.manager.last_name)
        message_for_volunteer = consts.VOLUNTEER_INTRODUCTION_STR.format(self.volunteer.first_name,
                                                                                     self.student.first_name,
                                                                                     self.student.last_name,
                                                                                     self.manager.first_name,
                                                                                     self.manager.last_name)
        email_to_student = Email(
            subject=subject,
            message=message_for_student,
            dst_address=self.student.email)

        email_to_volunteer = Email(
            subject=subject,
            message=message_for_volunteer,
            dst_address=self.volunteer.email
        )

        MailBox(self.manager).send_emails([email_to_student, email_to_volunteer])

    def send_reminder(self, time_passed) -> Match:
        """returns match with value of first/second remider sent updated"""
        if not self.first_reminder_sent:
            self.first_reminder_sent = True
        else:
            self.second_reminder_sent = True

        subject = "Reminder about native speakers program"
        
        message_for_student = consts.REMINDER_STR.format(self.student.first_name, 
                                                         self.volunteer.first_name, 
                                                         time_passed, 
                                                         self.manager.first_name,
                                                         self.manager.last_name)
        message_for_volunteer = consts.REMINDER_STR.format(self.volunteer.first_name, 
                                                           self.student.first_name, 
                                                           time_passed, 
                                                           self.manager.first_name,
                                                           self.manager.last_name)
        
        email_to_student = Email(
            subject=subject,
            message=message_for_student,
            dst_address=self.student.email
        )

        email_to_volunteer = Email(
            subject=subject,
            message=message_for_volunteer,
            dst_address=self.volunteer.email
        )

        MailBox(self.manager).send_emails([email_to_student, email_to_volunteer])

        return self

    def send_cancelation_messages(self):
        subject = "Native Speakers Program Dematch"

        message_for_student = consts.CANCELATION_STR.format(self.student.first_name, 
                                                         self.volunteer.first_name, 
                                                         self.volunteer.first_name, 
                                                         self.manager.first_name,
                                                         self.manager.last_name)
        message_for_volunteer = consts.CANCELATION_STR.format(self.volunteer.first_name, 
                                                           self.student.first_name, 
                                                           self.student.last_name, 
                                                           self.manager.first_name,
                                                           self.manager.last_name)

        email_to_student = Email(
            subject=subject,
            message=message_for_student,
            dst_address=self.student.email,
        )

        email_to_volunteer = Email(
            subject=subject,
            message=message_for_volunteer,
            dst_address=self.volunteer.email,
        )

        MailBox(self.manager).send_emails([email_to_student, email_to_volunteer])


class DbHandler():
    def __init__(self, db_file_name: str = consts.DEFAULT_DB_FILE_NAME) -> None:
        self.db_file_name = db_file_name
        self.db_content = {"students": [], "volunteers": [], "matches": []}
        self.db_content["students"]: List[Student] = self.get_students_from_db()
        self.db_content["volunteers"]: List[Volunteer] = self.get_volunteers_from_db()
        self.db_content["matches"]: List[Match] = self.get_matches_from_db()

    def send_reminder_all_matches(self):
        updated_matches = []
        for match in self.db_content["matches"]:
            year_started, month_started, day_started = match.date
            time_passed = datetime.now() - datetime(year_started, month_started, day_started)
            updated_match = match.send_reminder(time_passed.days)
            updated_matches.append(updated_match)
        self.add_objects_to_db(updated_matches)
    
    def encode_db_content(self) -> Dict[str, List[Any]]:
        encoded_students = [student.to_dict() for student in self.db_content["students"]]
        encoded_volunteers = [volunteer.to_dict() for volunteer in self.db_content["volunteers"]]
        encoded_matches = [match.to_dict() for match in self.db_content["matches"]]
        
        return {"students": encoded_students, "volunteers": encoded_volunteers, "matches": encoded_matches}

    def write_db_content_to_db(self) -> None:
        encoded_db_content = self.encode_db_content()
        
        with open(self.db_file_name, 'w') as db:
            db.write(json.dumps(encoded_db_content, indent = 4))
    
    def add_object_to_db(self, obj) -> None:

        if isinstance(obj, Student):
            with suppress(ValueError):
                self.db_content["students"].remove(obj)
            self.db_content["students"].append(obj)
        elif isinstance(obj, Match):
            with suppress(ValueError):
                self.db_content["matches"].remove(obj)
            self.db_content["matches"].append(obj)
        elif isinstance(obj, Volunteer):
            with suppress(ValueError):
                self.db_content["volunteers"].remove(obj)
            self.db_content["volunteers"].append(obj)

        else:
            return

        self.write_db_content_to_db()

    def add_objects_to_db(self, objects) -> None:
        for obj in objects:
            self.add_object_to_db(obj)

    def get_objects_list_from_db(self, obj_class, obj_name: str):
        with open(self.db_file_name, 'r') as db:
            try:
                db_content = json.loads(db.read())
            except:
                # file is empty
                db_content = self.db_content
            return [obj_class.from_dict(obj) for obj in db_content[obj_name]]
    
    def get_students_from_db(self) -> List[Match]:
        return self.get_objects_list_from_db(Student, "students")

    def get_volunteers_from_db(self) -> List[Match]:
        return self.get_objects_list_from_db(Volunteer, "volunteers")

    def get_matches_from_db(self) -> List[Match]:
        return self.get_objects_list_from_db(Match, "matches")

    def get_match_by_student(self, student: Student, matches= None) -> Match:
        if matches is None:
            matches = self.db_content["matches"]
        
        for match in matches:
            if match.student == student:
                return match
        return None

    def get_match_by_volunteer(self, volunteer: Volunteer, matches = None) -> Match:
        if matches is None:
            matches = self.db_content["matches"]

        for match in matches:
            if match.volunteer == volunteer:
                return match
        return None
    
    def delete_all_students(self):
        self.db_content["students"] = []
        self.write_db_content_to_db()

    def delete_student(self, student: Student):
        self.db_content["students"].remove(Student)
        self.write_db_content_to_db()

    def delete_volunteer(self, volunteer: Volunteer):
        self.db_content["volunteers"].remove(volunteer)
        self.write_db_content_to_db()

    def delete_all_matches(self):
        self.db_content["matches"] = []
        self.write_db_content_to_db()

    def delete_match(self, match: Match):
        self.db_content["matches"].remove(match)
        self.write_db_content_to_db()

@dataclass
class Email():
    subject: str
    message: str
    dst_address: str

    def __post_init__(self):
        self.subject = consts.MESSAGE_SUBJECT.format(self.subject)


@dataclass
class MailBox():
    manager: Manager
    port: int = 465
    smtp_email: str = "smtp.gmail.com"
    context: ssl.SSLContext = ssl.create_default_context()

    def send_emails(self, emails: List[Email]) -> None:
        with smtplib.SMTP_SSL(self.smtp_email, self.port, context=self.context) as server:
            server.login(self.manager.email, self.manager.password)
            for email in emails:
                server.sendmail(
                    self.manager.email,
                    email.dst_address,
                    email.subject + email.message
                )

class Matcher():
    def __init__(self, manager: Manager) -> None:
        self.manager = manager
        self.dbHandler: DbHandler = DbHandler()
        self.new_matches: List[Match] = []
        self.matches: List[Match] = self.dbHandler.db_content["matches"]

    def match_and_show(self) -> List[Match]:
        students = self.dbHandler.db_content["students"]
        volunteers = self.dbHandler.db_content["volunteers"]

        print("New Matches:\n")
        # search volunteer for each student
        for student in students:
            if self.dbHandler.get_match_by_student(student, self.matches) is not None:
                # match exists for student
                continue
            for volunteer in volunteers:
                if self.dbHandler.get_match_by_volunteer(volunteer, self.matches) is not None:
                    # volunteer is taken
                    continue
                new_match = Match(self.manager, student, volunteer)
                self.matches.append(new_match)
                self.new_matches.append(new_match)
                print(new_match)
                break

        if len(volunteers) > len(students):
            print(f"\n\n{len(volunteers) - len(students)} volunteers left without a student")

        elif len(volunteers) < len(students):
            print(f"\n\n{len(students) - len(volunteers)} students left without a volunteer\n")

        else:
            print(f"\n\nAll students and volunteers coupled\n")

        return self.new_matches
