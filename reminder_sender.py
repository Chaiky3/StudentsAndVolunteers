from datetime import datetime, timedelta

import consts
from objects import DbHandler, Match, wait_for_internet_connection

def report_to_logger(message: str):
    with open("reminders.log", 'a') as logger:
        logger.write(f"\n{message}")


def needs_to_send_reminder(match: Match, time_passed: timedelta):
    report_to_logger(f"{datetime.now()}: Checking start date for {match.volunteer.first_name} and {match.student.first_name}.")
    return (time_passed.days > consts.DAYS_UNTIL_FIRST_EMAIL and not match.first_reminder_sent) or \
        (time_passed.days > consts.DAYS_UNTIL_SECOND_EMAIL and not match.second_reminder_sent)

def send_reminder_to_match(match: Match, time_passed: timedelta):
    report_to_logger(f"{datetime.now()}: Sending reminder to {match.student.first_name} and {match.volunteer.first_name}\nIt's been {time_passed.days} days.")
    updated_match = match.send_reminder(time_passed.days)
    report_to_logger(f"{datetime.now()}: Reminder sent {match.student.first_name} and {match.volunteer.first_name}.")
    return updated_match

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
        if needs_to_send_reminder(match, time_passed):
            updated_matches.append(send_reminder_to_match(match, time_passed))

        elif time_passed.days > consts.DAYS_UNTIL_DELETION:
            dbHandler.delete_all_matches()
            dbHandler.delete_all_students()
            exit()
 
    dbHandler.add_objects_to_db(updated_matches)

if __name__ == '__main__':
    send_reminders()