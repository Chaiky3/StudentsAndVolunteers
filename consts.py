DEFAULT_DB_FILE_NAME = "db.json"
DEFAULT_DB_CONTENT = {"students": {}, "volunteers": {}, "matches": {}}

DAYS_BETWEEN_REMINDERS = 14
DAYS_UNTIL_DELETION = 365
DAY_IN_SECS = 86400

MESSAGE_SUBJECT = "Subject: {}\n\n"

# html format

STUDENT_INTRODUCTION_STR = """
<div dir="ltr" style="text-align: left;"><p>
<h4>Dear {0}</h4><br>

I am glad you signed up for the native speakers program.<br><br>

Please read the following guidelines carefully:<br>

https://docs.google.com/document/d/1SdHe98UghKRDFJTS_vrCMOGPdTabw5Yasc9fUcg3giU/edit?usp=sharing<br><br>

After reading this, please contact:<br>
{1} {2}<br>
{3}<br>
{4}<br><br>

{5} {6}
</p></div>
"""

VOLUNTEER_INTRODUCTION_STR = """
<div dir="ltr" style="text-align: left;"><p>
<h4>Dear {0}!</h4><br>

Thank you for agreeing to speak on a regular basis with my students in order to help them improve their oral proficiency.<br><br>

I have given your contact information to {1} {2} who will hopefully contact you soon.<br>

If you do not hear from {1}, please let me know and I will hook you up with someone else.<br><br>

Your willingness to invest time in these students means a lot. These students will eventually become English teachers and will teach the next generation of Israelis, so your help will impact the national level of oral proficiency in Israel!<br><br>

THANK YOU<br><br>

{3} {4}
</p></div>
"""

REMINDER_STR = """
<div dir="ltr" style="text-align: left;"><p>
<h4>Dear {0}</h4><br>

You have now been in contact with {1} for {2} days.<br>

I would like to hear a bit how it's going. Are you happy with the match? Is there anything you need from me?<br><br>

Please let me know.<br><br>

All the best,<br><br>

{3} {4}
</p></div>
"""

CANCELATION_STR = """
<div dir="ltr" style="text-align: left;"><p>
<h4>Dear {0}</h4><br>

You will not be in touch with {1} {2} anymore.<br>

After a bit of thinking, I decided to cancel the match. If relvant, I will work to find you another match asap.<br><br>

All the best,<br><br>

{3} {4}
</p></div>
"""
