from typing import Dict
from datetime import datetime, timedelta

import consts

from objects import DbHandler, Match
from utils import wait_for_internet_connection


def report_to_logger(message: str):
    with open("reminders.log", 'a') as logger:
        logger.write(f"\n{message}")


def needs_to_send_reminder(match: Match, time_passed: timedelta):
    dbHandler = DbHandler()
    student = dbHandler.get_student_by_id(match.student_id)
    volunteer = dbHandler.get_volunteer_by_id(match.volunteer_id)
    
    report_to_logger(f"{datetime.now()}: Checking start date for {student.first_name} and {volunteer.first_name}.")
    return match.num_of_reminders_sent < time_passed.days // consts.DAYS_BETWEEN_REMINDERS


def send_reminder_to_match(match: Match, time_passed: timedelta):
    dbHandler = DbHandler()
    student = dbHandler.get_student_by_id(match.student_id)
    volunteer = dbHandler.get_volunteer_by_id(match.volunteer_id)
    
    report_to_logger(f"{datetime.now()}: Sending reminder to {student.first_name} and {volunteer.first_name}\nIt's been {time_passed.days} days.")
    match.send_reminder(time_passed.days)
    report_to_logger(f"{datetime.now()}: Reminder sent to {student.first_name} and {volunteer.first_name}.")


def send_reminders():
    wait_for_internet_connection()
    time_now = datetime.now()
    if time_now.weekday() in (4, 5):
        report_to_logger(f"{datetime.now()}: Friday, not sending notifications")
        return
    dbHandler = DbHandler()
    matches: Dict[int, Match] = dbHandler.get_matches_from_db()
    updated_matches = {}
    for match_id, match in matches.items():
        time_passed = time_now - datetime(*match.date)
        if needs_to_send_reminder(match, time_passed):
            send_reminder_to_match(match, time_passed)
            match.num_of_reminders_sent += 1
            updated_matches[match_id] = match

        elif time_passed.days > consts.DAYS_UNTIL_DELETION:
            report_to_logger(f"Deleting all matches and students because {consts.DAYS_UNTIL_DELETION} days have passed")
            dbHandler.delete_all_matches()
            dbHandler.delete_all_students()
            exit()
 
    dbHandler.update_object_in_db(updated_matches)


if __name__ == '__main__':
    send_reminders()