from time import sleep
from datetime import datetime

import consts
from objects import DbHandler, wait_for_internet_connection


def send_reminders():
    wait_for_internet_connection()
    time_now = datetime.now()
    if time_now.weekday() in (4, 5):
        print(f"{datetime.now()}: Friday, not sending notifications")
        return
    dbHandler = DbHandler()
    matches = dbHandler.db_content["matches"]
    updated_matches = []
    for match in matches:
        time_passed = time_now - datetime(*match.date)
        if (time_passed.days > consts.DAYS_UNTIL_FIRST_EMAIL and not match.first_reminder_sent) or \
            (time_passed.days > consts.DAYS_UNTIL_SECOND_EMAIL and not match.second_reminder_sent):
            print(f"{datetime.now()}: Sending reminder to {match.student.first_name} and {match.volunteer.first_name}")
            updated_match = match.send_reminder(time_passed.days)
            print(f"{datetime.now()}: Reminder sent {match.student.first_name} and {match.volunteer.first_name}")
            updated_matches.append(updated_match)
        elif time_passed.days > consts.DAYS_UNTIL_DELETION:
            dbHandler.delete_all_matches()
            dbHandler.delete_all_students()
            exit()
    dbHandler.add_objects_to_db(updated_matches)

if __name__ == '__main__':
    send_reminders()