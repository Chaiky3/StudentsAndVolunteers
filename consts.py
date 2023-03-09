DEFAULT_DB_FILE_NAME = "db.json"
DEFAULT_DB_CONTENT = {"students": {}, "volunteers": {}, "matches": {}}

DAYS_BETWEEN_REMINDERS = 14
DAYS_UNTIL_DELETION = 365
DAY_IN_SECS = 86400

MESSAGE_SUBJECT = "Subject: {}\n\n"

STUDENT_INTRODUCTION_STR = """
Dear {0},

I am glad you signed up for the native speakers program.

Please read the following guidelines carefully:

https://docs.google.com/document/d/1SdHe98UghKRDFJTS_vrCMOGPdTabw5Yasc9fUcg3giU/edit?usp=sharing

After reading this, please contact:
{1} {2}
{3}
{4}

{5} {6}
"""

VOLUNTEER_INTRODUCTION_STR = """
Dear {0}!

Thank you for agreeing to speak on a regular basis with my students in order to help them improve their oral proficiency.

I have given your contact information to {1} {2} who will hopefully contact you soon.

If you do not hear from {1}, please let me know and I will hook you up with someone else.

Your willingness to invest time in these students means a lot. These students will eventually become English teachers and will teach the next generation of Israelis, so your help will impact the national level of oral proficiency in Israel!

THANK YOU

{3} {4}
"""

REMINDER_STR = """
Dear {0},

You have now been in contact with {1} for {2} days.

I would like to hear a bit how it's going. Are you happy with the match? Is there anything you need from me?

Please let me know.

All the best,

{3} {4}
"""

CANCELATION_STR = """
Dear {0},

You will not be in touch with {1} {2} anymore.

After a bit of thinking, I decided to cancel the match. If relvant, I will work to find you another match asap.

All the best,

{3} {4}
"""
