from __future__ import annotations

import os
import json
import pathlib

from enum import Enum, auto
from datetime import datetime
from mailjet_rest import Client
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List, Dict, Tuple, Any, Optional, Union

import consts
import managerCredentials

from utils import get_safe_user_input, press_any_key


@dataclass_json
@dataclass
class Writeable():
    pass

@dataclass
class Human(Writeable):
    first_name: str
    last_name: str
    email: str = field()

    def __repr__(self) -> str:
        return f"""
        name: {self.first_name} {self.last_name}
        email: {self.email}
        """

@dataclass(unsafe_hash=True)
class Student(Human):
    talksWithGirls: bool

    def __repr__(self) -> str:
        return super().__repr__() + f"""talks with girls: {self.talksWithGirls}
        """

    @staticmethod
    def interactive() -> Student:
        params = []
        for attr in ("First Name", "Last Name", "Email", "talks with girls [Y/n]"):
            user_input = input(f"Enter {attr}: ")
            if user_input == "e":
                return
            if attr == "talks with girls [Y/n]":
                user_input = user_input != "n"

            params.append(user_input)

        return Student(*params)

@dataclass(unsafe_hash=True)
class Volunteer(Human):
    isGirl: bool
    phone: str

    def __repr__(self) -> str:
        return super().__repr__() + f"""phone: {self.phone}
        is girl: {self.isGirl}
        """

    @staticmethod
    def interactive() -> Volunteer:
        params = []
        for attr in ("First Name", "Last Name", "Email", "Is Girl [y/N]", "Phone Number"):
            user_input = input(f"Enter {attr}: ")
            if user_input == "e":
                return
            if attr == "Is Girl [y/N]":
                user_input = user_input == "y"

            params.append(user_input)
        
        return Volunteer(*params)


@dataclass(unsafe_hash=True)
class Manager(Human):
    apikey: str
    apisecretkey: str


@dataclass(unsafe_hash=True)
class Match(Writeable):
    student_id: int
    volunteer_id: int
    date: Tuple[int, int] = datetime.now().year, datetime.now().month, datetime.now().day
    num_of_reminders_sent: int = 0

    def __repr__(self) -> str:
        student = DbHandler().get_student_by_id(self.student_id)
        volunteer = DbHandler().get_volunteer_by_id(self.volunteer_id)
        
        return f"{student.first_name} {student.last_name} <--> {volunteer.first_name} {volunteer.last_name}"
    
    def __contains__(self, id: int) -> bool:
        return id in (self.student_id, self.volunteer_id)

    def send_introduction_message(self) -> None:
        manager = Manager(managerCredentials.MANAGER_FIRST_NAME,
                          managerCredentials.MANAGER_LAST_NAME,
                          managerCredentials.MANAGER_EMAIL,
                          managerCredentials.MANAGER_API_KEY,
                          managerCredentials.MANAGER_API_SECRET)
        student = DbHandler().get_student_by_id(self.student_id)
        volunteer = DbHandler().get_volunteer_by_id(self.volunteer_id)

        subject = "Introduction to native speakers program"

        message_for_student = consts.STUDENT_INTRODUCTION_STR.format(student.first_name,
                                                                     volunteer.first_name,
                                                                     volunteer.last_name,
                                                                     volunteer.phone,
                                                                     volunteer.email,
                                                                     manager.first_name,
                                                                     manager.last_name)
        message_for_volunteer = consts.VOLUNTEER_INTRODUCTION_STR.format(volunteer.first_name,
                                                                         student.first_name,
                                                                         student.last_name,
                                                                         manager.first_name,
                                                                         manager.last_name)
        email_to_student = Email(
            subject=subject,
            message=message_for_student,
            dst_address=student.email)

        email_to_volunteer = Email(
            subject=subject,
            message=message_for_volunteer,
            dst_address=volunteer.email
        )

        MailBox(manager).send_emails([email_to_student, email_to_volunteer])

    def send_reminder(self, time_passed) -> None:
        subject = "Reminder about native speakers program"

        student = DbHandler().get_student_by_id(self.student_id)
        volunteer = DbHandler().get_volunteer_by_id(self.volunteer_id)
        manager = Manager(managerCredentials.MANAGER_FIRST_NAME,
                          managerCredentials.MANAGER_LAST_NAME,
                          managerCredentials.MANAGER_EMAIL,
                          managerCredentials.MANAGER_API_KEY,
                          managerCredentials.MANAGER_API_SECRET)

        message_for_student = consts.REMINDER_STR.format(student.first_name, 
                                                         volunteer.first_name, 
                                                         time_passed, 
                                                         manager.first_name,
                                                         manager.last_name)
        message_for_volunteer = consts.REMINDER_STR.format(volunteer.first_name, 
                                                           student.first_name, 
                                                           time_passed, 
                                                           manager.first_name,
                                                           manager.last_name)
        
        email_to_student = Email(
            subject=subject,
            message=message_for_student,
            dst_address=student.email
        )

        email_to_volunteer = Email(
            subject=subject,
            message=message_for_volunteer,
            dst_address=volunteer.email
        )

        MailBox(manager).send_emails([email_to_student, email_to_volunteer])

    def send_cancelation_messages(self):
        subject = "Native Speakers Program Dematch"

        student = DbHandler().get_student_by_id(self.student_id)
        volunteer = DbHandler().get_volunteer_by_id(self.volunteer_id)
        manager = Manager(managerCredentials.MANAGER_FIRST_NAME,
                          managerCredentials.MANAGER_LAST_NAME,
                          managerCredentials.MANAGER_EMAIL,
                          managerCredentials.MANAGER_API_KEY,
                          managerCredentials.MANAGER_API_SECRET)
        
        message_for_student = consts.CANCELATION_STR.format(student.first_name, 
                                                            volunteer.first_name, 
                                                            volunteer.first_name, 
                                                            manager.first_name,
                                                            manager.last_name)
        message_for_volunteer = consts.CANCELATION_STR.format(volunteer.first_name, 
                                                              student.first_name, 
                                                              student.last_name, 
                                                              manager.first_name,
                                                              manager.last_name)

        email_to_student = Email(
            subject=subject,
            message=message_for_student,
            dst_address=student.email,
        )

        email_to_volunteer = Email(
            subject=subject,
            message=message_for_volunteer,
            dst_address=volunteer.email,
        )

        MailBox(manager).send_emails([email_to_student, email_to_volunteer])


class DbHandler():
    def __init__(self, db_file_name: str = consts.DEFAULT_DB_FILE_NAME) -> None:
        self.db_content = consts.DEFAULT_DB_CONTENT
        self.db_file_path = os.path.join(pathlib.Path(__file__).parent.resolve(), db_file_name)
        
        self.create_db(db_file_name)
        
        self.db_content["students"]: Dict[int, Student] = self.get_students_from_db()
        self.db_content["volunteers"]: Dict[int, Volunteer] = self.get_volunteers_from_db()
        self.db_content["matches"]: Dict[int, Match] = self.get_matches_from_db()

    def create_db(self, db_file_name: str):
        if not os.path.isfile(self.db_file_path):
            self.write_db_content_to_db()

    def get_objects_from_db(self, obj_class, obj_name: str) -> Dict[int, Union[Student, Volunteer, Match]]:
        with open(self.db_file_path, 'r') as db:
            db_content = json.loads(db.read())

        return {obj_id: obj_class.from_dict(obj) for obj_id, obj in db_content[obj_name].items()}

    def get_students_from_db(self) -> Dict[int, Match]:
        return self.get_objects_from_db(Student, "students")

    def get_volunteers_from_db(self) -> Dict[int, Match]:
        return self.get_objects_from_db(Volunteer, "volunteers")

    def get_matches_from_db(self) -> Dict[int, Match]:
        return self.get_objects_from_db(Match, "matches")

    def get_student_by_id(self, student_id) -> Student:
        return self.db_content["students"][student_id]

    def get_volunteer_by_id(self, volunteer_id) -> Volunteer:
        return self.db_content["volunteers"][volunteer_id]

    def get_match_by_id(self, match_id) -> Match:
        return self.db_content["matches"][match_id]

    def encode_db_content(self) -> Dict[str, Dict[str, Dict[int, Union[Student, Volunteer, Match]]]]:
        encoded_students = {student_id: student.to_dict() for student_id, student in self.db_content["students"].items()}
        encoded_volunteers = {volunteer_id: volunteer.to_dict() for volunteer_id, volunteer in self.db_content["volunteers"].items()}
        encoded_matches = {match_id: match.to_dict() for match_id, match in self.db_content["matches"].items()}

        return {"students": encoded_students, "volunteers": encoded_volunteers, "matches": encoded_matches}

    def write_db_content_to_db(self) -> None:
        encoded_db_content = self.encode_db_content()

        with open(self.db_file_path, 'w') as db:
            db.write(json.dumps(encoded_db_content, indent = 4))
    
    def add_object_to_db(self, obj: Optional[Dict[int, Union[Student, Volunteer, Match]]], object_id: Optional[int] = None) -> None:
        if not obj:
            return

        object_id = object_id if object_id else hash(obj)  # support adding and updating

        if isinstance(obj, Student):
            self.db_content["students"][object_id] = obj
        elif isinstance(obj, Match):
            self.db_content["matches"][object_id] = obj
        elif isinstance(obj, Volunteer):
            self.db_content["volunteers"][object_id] = obj

        else:
            raise TypeError(f"can't add object type {type(obj)} to db")

        self.write_db_content_to_db()

    def add_objects_to_db(self, objects: List[Union[Student, Volunteer, Match]]) -> None:
        for obj in objects:
            self.add_object_to_db(obj)

    def update_object_in_db(self, objects: Dict[int, Union[Student, Volunteer, Match]]) -> None:
        for obj_id, obj in objects.items():
            self.add_object_to_db(obj, obj_id)

    def get_match_id(self, student_id: int = None, volunteer_id: int = None) -> Optional[int]:
        if not student_id and not volunteer_id:
            return None

        for match_id, match in self.db_content["matches"].items():
            if student_id and volunteer_id:
                if match.student_id == student_id and match.volunteer_id == volunteer_id:
                    return match_id

            elif student_id:
                if match.student_id == student_id:
                    return match_id
            
            else:
                if match.volunteer_id == volunteer_id:
                    return match_id

        return None

    def delete_all_students(self) -> None:
        self.db_content["students"] = {}
        self.write_db_content_to_db()

    def delete_student(self, student_id: int) -> None:
        del self.db_content["students"][student_id]
        self.write_db_content_to_db()

    def delete_volunteer(self, volunteer_id: int) -> None:
        del self.db_content["volunteers"][volunteer_id]
        self.write_db_content_to_db()

    def delete_all_matches(self) -> None:
        self.db_content["matches"] = {}
        self.write_db_content_to_db()

    def delete_match(self, match_id: int) -> None:
        del self.db_content["matches"][match_id]
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
    
    def __post_init__(self) -> None:
        self.mailjet = Client(auth=(self.manager.apikey, self.manager.apisecretkey), version='v3.1')

    def send_emails(self, emails: List[Email]) -> None:
        self.mailjet.send.create({
            'Messages': [
            {
                    "From": {
                            "Email": self.manager.email,
                            "Name": f"{self.manager.first_name} {self.manager.last_name}"
                    },
                    "To": [
                            {
                                    "Email": email.dst_address
                            }
                    ],
                    "Subject": email.subject,
                    "HTMLPart": email.message
            }
            for email in emails]
        })

class Matcher():
    def __init__(self, manager: Manager) -> None:
        self.manager = manager
        self.dbHandler: DbHandler = DbHandler()
        self.matches: List[Match] = list(self.dbHandler.db_content["matches"].values())

    def __get_free_students(self) -> Dict[int, Student]:
        existing_matches: Dict[int, Match] = self.dbHandler.db_content["matches"].values()
        existing_students = self.dbHandler.db_content["students"]
        free_students = {}

        for student_id, student in existing_students.items():
            if not any(student_id in match for match in existing_matches):
                free_students[student_id] = student

        return free_students
    
    def __get_free_volunteers(self) -> Dict[int, Volunteer]:
        existing_matches: Dict[int, Match] = self.dbHandler.db_content["matches"].values()
        existing_volunteer = self.dbHandler.db_content["volunteers"]
        free_volunteers = {}

        for volunteer_id, volunteer in existing_volunteer.items():
            if not any(volunteer_id in match for match in existing_matches):
                free_volunteers[volunteer_id] = volunteer

        return free_volunteers

    @staticmethod
    def check_that_there_is_no_gender_problem(student: Student, volunteer: Volunteer) -> bool:
        if (not volunteer.isGirl) or (student.talksWithGirls):
            return True
        
        if volunteer.isGirl and student.talksWithGirls:
            return True
        
        return False
    
    def auto_match_and_show(self) -> List[Match]:
        students = self.__get_free_students()
        volunteers = self.__get_free_volunteers()
        new_matches = []
        
        if not students or not volunteers:
            print("No free students or volunteers in the system...")
            return

        # search volunteer for each student
        for student_id, student in students.items():
            for volunteer_id, volunteer in volunteers.items():
                if not self.check_that_there_is_no_gender_problem(student, volunteer):
                    continue
                new_match = Match(student_id, volunteer_id)
                self.matches.append(new_match)
                new_matches.append(new_match)
                print(new_match)
                break

        if not new_matches:
            print("No possible new matches")

        if len(volunteers) > len(students):
            print(f"\n\n{len(volunteers) - len(students)} volunteers left without a student")

        elif len(volunteers) < len(students):
            print(f"\n\n{len(students) - len(volunteers)} students left without a volunteer\n")

        else:
            print(f"\n\nAll students and volunteers coupled\n")

        return new_matches

    def manual_match_and_show(self) -> List[Match]:
        students = self.__get_free_students()
        volunteers = self.__get_free_volunteers()
        students_index_to_id_map = []
        volunteers_index_to_id_map = []

        # check that there are at least 1 student and 1 volunteer
        if not students or not volunteers:
            print("No free students or volunteers in the system...")
            return

        # Choose student
        for index, (student_id, student) in enumerate(students.items()):
            students_index_to_id_map.append(student_id)
            print(f"{index}:    {student}")

        student_index = get_safe_user_input("Choose student number to match: ", input_type=int, expected_inputs=range(len(students)))

        if student_index is None:
            return

        student_id = students_index_to_id_map[int(student_index)]
        student = self.dbHandler.get_student_by_id(student_id)

        # choose volunteer
        for index, (volunteer_id, volunteer) in enumerate(volunteers.items()):
            volunteers_index_to_id_map.append(volunteer_id)
            print(f"{index}:    {volunteer}")

        volunteer_index = get_safe_user_input(f"Choose volunteer number to match: ", input_type=int, expected_inputs=range(len(volunteers)))

        if volunteer_index is None:
            return
        
        volunteer_id = volunteers_index_to_id_map[int(volunteer_index)]
        volunteer = self.dbHandler.get_volunteer_by_id(volunteer_id)

        if not self.check_that_there_is_no_gender_problem(student, volunteer):
            print(f"\nCan't match {student.first_name} with {volunteer.first_name} because of gender preference")
            return

        new_match = Match(student_id, volunteer_id)
        print(f"\n\nMatch:\n {new_match}")

        return [new_match]
