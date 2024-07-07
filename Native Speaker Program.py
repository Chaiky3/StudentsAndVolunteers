import customtkinter
import webbrowser

from CTkTable import *
from functools import partial
from typing import List

import managerCredentials

from objects import DbHandler, Student, Volunteer, Matcher, Manager, Match, Email, MailBox

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


MANAGER = Manager(managerCredentials.MANAGER_FIRST_NAME,
                  managerCredentials.MANAGER_LAST_NAME,
                  managerCredentials.MANAGER_EMAIL,
                  managerCredentials.MANAGER_API_KEY,
                  managerCredentials.MANAGER_API_SECRET)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Native Speakers Porgram")
        self.geometry(f"{1100}x{580}")
        self.resizable(False, False)

        # configure grid layout (4x4)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0,1), weight=1)

        # create sidebar frame and show
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=1, sticky="nsew")

        # create data frame
        self.data_frame = customtkinter.CTkFrame(self, bg_color="transparent")
        self.data_frame.grid(row=1, column=1, columnspan=3, sticky="nsew")
        self.data_frame.grid_columnconfigure((0,1,2), weight=1)

        # create left subdata frame
        self.left_data_frame = customtkinter.CTkFrame(self.data_frame, fg_color="transparent")
        self.left_data_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.left_data_frame.grid_rowconfigure(3, weight=1)

        # create middle subdata frame
        self.middle_data_frame = customtkinter.CTkFrame(self.data_frame, fg_color="transparent")
        self.middle_data_frame.grid(row=0, column=1, rowspan=5, sticky="nsew")

        # create right subdata frame
        self.right_data_frame = customtkinter.CTkFrame(self.data_frame, fg_color="transparent")
        self.right_data_frame.grid(row=0, column=2, rowspan=5, sticky="nsew")
        self.right_data_frame.grid_rowconfigure(2, weight=1)

        self.show_main_menu()
        
        # set shit
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")
        self.clicked = None

    def show_main_menu(self):
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Native speakers Program", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.destroy_data_widgets()
        self.student_button = customtkinter.CTkButton(self.sidebar_frame, command=partial(self.show_dashboard, "Student"), text="Students")
        self.student_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.volunteers_button = customtkinter.CTkButton(self.sidebar_frame, command=partial(self.show_dashboard, "Volunteer"), text="Volunteers")
        self.volunteers_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.matches_button = customtkinter.CTkButton(self.sidebar_frame, command=partial(self.show_dashboard, "Match"), text="Matches")
        self.matches_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.mailjet_button = customtkinter.CTkButton(self.sidebar_frame, command=self.open_mailjet_website, text="Open MailJet")
        self.mailjet_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

    # def popup_window(self, message):
    #     popup_window = customtkinter.CTkToplevel(self)
    #     popup_window.title("Pop Up Window")
    #     popup_window.geometry("200x100")
    #     popup_window.resizable(False, False)
    #     popup_window.wm_transient(app)
    #     popup_label = customtkinter.CTkLabel(popup_window, text=message)
    #     popup_label.grid(row=0, column=0)
    #     popup_approve_button = customtkinter.CTkButton(popup_window, text="OK")
    #     popup_approve_button.grid(row=1, column=0)
    
    def show_dashboard(self, type: str):
        if type == "Student": 
            self.student_button.configure(state="disabled")
            self.volunteers_button.configure(state="normal")
            self.matches_button.configure(state="normal")
        if type == "Volunteer": 
            self.student_button.configure(state="normal")
            self.volunteers_button.configure(state="disabled"),
            self.matches_button.configure(state="normal")
        if type == "Match": 
            self.student_button.configure(state="normal")
            self.volunteers_button.configure(state="normal"),
            self.matches_button.configure(state="disabled")

        self.destroy_data_widgets()
        self.show_data(type)
        self.show_add_or_match(type)
        self.show_remove(type)
        self.show_send_email(type)

    def destroy_data_widgets(self):
        for frame in (self.scrollable_frame, self.left_data_frame, self.middle_data_frame, self.right_data_frame):
            for widget in frame.winfo_children():
                widget.grid_forget()

    def show_data(self, type):
        try:
            self.table.destroy()
        except:
            pass
        db_handler = DbHandler()
        db = {
            "Student": db_handler.get_students_from_db(table_format=True),
            "Volunteer": db_handler.get_volunteers_from_db(table_format=True),
            "Match": db_handler.get_matches_from_db(table_format=True)
        }.get(type)
        columns = len(db[0]) if len(db) else 4
        self.table = CTkTable(self.scrollable_frame, row=len(db), column=columns, values=db, hover=True, width=760/columns)
        self.table.grid(row=0, column=1, padx=(10, 10), pady=(20, 0))

    def show_add_or_match(self, type):
        if type == "Match":
            self.show_match()
        else:
            self.show_add(type)
    
    def show_add(self, type: str) -> None:
        def add_action():
            obj_type = Student if type == "Student" else Volunteer
            new_obj = obj_type(*[attr.get() for attr in add_widgets])

            # override boolean attrs
            if type == "Student":
                new_obj.talksWithGirls = new_obj.talksWithGirls == "Talks to girls"
            if type == "Volunteer":
                new_obj.isGirl = new_obj.isGirl == "Female"
            
            # make sure that none of the fields are empty
            if any(attr == "" for attr in [new_obj.first_name, new_obj.last_name, new_obj.email]):
                return
            if type == "Volunteer" and new_obj.phone == "":
                return
            
            DbHandler().add_object_to_db(new_obj)
            
            # update screen
            self.show_data(type)
            self.show_remove(type)
            self.show_send_email(type)
            first_name.delete(0, 'end')
            last_name.delete(0, 'end')
            email.delete(0, 'end')
            if type == "Volunteer":
                phone_number.delete(0, 'end')

        add_widgets = []
        add_label = customtkinter.CTkLabel(self.left_data_frame, text=f"Add a {type}", font=customtkinter.CTkFont(size=20, weight="bold"))
        add_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        first_name = customtkinter.CTkEntry(self.left_data_frame, placeholder_text="First Name", width=180)
        add_widgets.append(first_name)
        last_name = customtkinter.CTkEntry(self.left_data_frame, placeholder_text="Last Name", width=180)
        add_widgets.append(last_name)
        email = customtkinter.CTkEntry(self.left_data_frame, placeholder_text="Email", width=180)
        add_widgets.append(email)
        if type == "Student":
            talks_to_girls = customtkinter.CTkSegmentedButton(self.left_data_frame, values=["Talks to girls", "Doesn't talk to girls"], width=180)
            talks_to_girls.set("Talks to girls")
            add_widgets.append(talks_to_girls)

        elif type == "Volunteer":
            add_widgets.append(customtkinter.CTkSegmentedButton(self.left_data_frame, values=["Male", "Female"]))
            phone_number = customtkinter.CTkEntry(self.left_data_frame, placeholder_text="Phone Number", width=180)
            add_widgets.append(phone_number)

        for index, widget in enumerate(add_widgets):
            widget.grid(row=index + 1, column=0, padx=20, pady=(7,7))
        
        submit_button = customtkinter.CTkButton(self.left_data_frame, text="Submit", command=add_action)
        submit_button.grid(row=len(add_widgets)+1, column=0, padx=20, pady=(30,10))

    def show_remove(self, type):
        def remove_action():
            name = name_to_delete.get()
            
            if not name:
                return
            
            db_handler = DbHandler()
            id_to_delete = {
                "Student": db_handler.get_student_id_by_name,
                "Volunteer": db_handler.get_volunteer_id_by_name,
                "Match": db_handler.get_match_id_by_name
            }.get(type)(name)

            if name.startswith("All "):
                db_handler.delete_all_matches()
                delete_function = {
                    "Student": db_handler.delete_all_students,
                    "Volunteer": db_handler.delete_all_volunteers,
                    "Match": db_handler.delete_all_matches
                }.get(type)
                delete_function()
            else:
                delete_function = {
                    "Student": db_handler.delete_student,
                    "Volunteer": db_handler.delete_volunteer,
                    "Match": db_handler.delete_match
                }.get(type)

                if type != "Match":
                    args = {
                        "Student": {"student_id": id_to_delete},
                        "Volunteer": {"volunteer_id": id_to_delete}
                    }.get(type)
                    match_id = db_handler.get_match_id(**args)
                    if match_id:
                        db_handler.delete_match(match_id)

                delete_function(id_to_delete)

            # refresh page
            name_to_delete.configure(values=get_available_names_to_delete())
            self.show_data(type)
            self.show_add_or_match(type)
            self.show_send_email(type)

        def get_available_names_to_delete():
            return {
                "Student": ["All Students"] + db_handler.get_students_names(),
                "Volunteer": ["All Volunteers"] + db_handler.get_volunteers_names(),
                "Match": ["All Matches"] + db_handler.get_matches_names()
            }[type]

        db_handler = DbHandler()
        remove_label = customtkinter.CTkLabel(self.middle_data_frame, text=f"Remove a {type}", font=customtkinter.CTkFont(size=20, weight="bold"))
        remove_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        name_to_delete = customtkinter.CTkComboBox(self.middle_data_frame, values=get_available_names_to_delete(), width=220)
        name_to_delete.grid(row=1, column=0, padx=20, pady=(7,7))

        remove_button = customtkinter.CTkButton(self.middle_data_frame, command=remove_action, text="Remove")
        remove_button.grid(row=5, column=0, padx=20, pady=10, sticky="s")

    def show_send_email(self, type):
        def send_command(addressee: str, email_subject: str, emails_content: List[str]):
            email_subject = email_subject.get()
            if not all(chr.isalpha() or chr.isspace() for chr in email_subject):
                return

            emails = []
            students_addressees = []
            volunteers_addresees = []
            db_handler = DbHandler()
            if type == "Student":
                if addressee.get().startswith("All "):
                    students_addressees = db_handler.get_students_from_db().values()
                else:
                    students_addressees.append(db_handler.get_student_by_name(addressee.get()))
            elif type == "Volunteer":
                if addressee.get().startswith("All "):
                    volunteers_addresees = db_handler.get_volunteers_from_db().values()
                else:
                    volunteers_addresees.append(db_handler.get_volunteer_by_name(addressee.get()))
            elif type == "Match":
                if addressee.get().startswith("All "):
                    for match in db_handler.get_matches_from_db().values():
                        students_addressees.append(match.get_student())
                        volunteers_addresees.append(match.get_volunteer())
                else:
                    match = db_handler.get_match_by_name(addressee.get())
                    students_addressees.append(match.get_student())
                    volunteers_addresees.append(match.get_volunteer())

            if type in ("Student", "Volunteer"):
                assert len(emails_content) == 1
                email_content = emails_content[0].get("0.0", "end").replace("\n", "<br>")

                email_addresses = [human.email for human in students_addressees or volunteers_addresees]
                for address in email_addresses:
                    emails.append(Email(email_subject, email_content, address))

            if type == "Match":
                # first student and then volunteer
                assert len(emails_content) == 2
                email_to_student_content = emails_content[0].get("0.0", "end").replace("\n", "<br>")
                email_to_volunteer_content = emails_content[1].get("0.0", "end").replace("\n", "<br>")

                for student_addressee in students_addressees:
                    emails.append(Email(email_subject, email_to_student_content, student_addressee.email))
                for volunteer_addressee in volunteers_addresees:
                    emails.append(Email(email_subject, email_to_volunteer_content, volunteer_addressee.email))

            print(emails)
            # MailBox(MANAGER).send_emails(emails)

        send_email_label = customtkinter.CTkLabel(self.right_data_frame, text="Send Email To", font=customtkinter.CTkFont(size=20, weight="bold"))
        send_email_label.grid(row=0, column=1, padx=20, pady=(20, 20))

        db_handler = DbHandler()
        options_to_send_to = {
            "Student": ["All Students"] + db_handler.get_students_names(),
            "Volunteer": ["All Volunteers"] + db_handler.get_volunteers_names(),
            "Match": ["All Matches"] + db_handler.get_matches_names()
        }.get(type)
        name_to_send_email_to = customtkinter.CTkComboBox(self.right_data_frame, values=options_to_send_to, width=220)
        name_to_send_email_to.grid(row=1, column=1, padx=20, pady=(7,7))

        email_subject = customtkinter.CTkEntry(self.right_data_frame, placeholder_text="Email Subject", width=180)
        email_subject.grid(row=2, column=1, padx=20, pady=(7,7))

        emails_content = []
        if type == "Match":
            email_to_student_content = customtkinter.CTkTextbox(self.right_data_frame, width=180, height=65)
            email_to_student_content.insert("end", "Dear student...")
            email_to_student_content.grid(row=3, column=1, padx=20, pady=(7,7))
            emails_content.append(email_to_student_content)
            
            email_to_volunteer_content = customtkinter.CTkTextbox(self.right_data_frame, width=180, height=65)
            email_to_volunteer_content.insert("end", "Dear volunteer...")
            email_to_volunteer_content.grid(row=4, column=1, padx=20, pady=(7,7))
            emails_content.append(email_to_volunteer_content)
        else:
            email_content = customtkinter.CTkTextbox(self.right_data_frame, width=180, height=120)
            email_content.grid(row=3, column=1, padx=20, pady=(7,7))
            emails_content.append(email_content)

        send_button = customtkinter.CTkButton(self.right_data_frame, command=lambda: send_command(name_to_send_email_to, email_subject, emails_content), text="Send")
        send_button.grid(row=5, column=1, padx=20, pady=(30,10), sticky="s")

    def show_match(self, method="auto"):
        for widget in self.left_data_frame.winfo_children():
            widget.destroy()

        def suggest_auto_match():
            for new_match in Matcher(MANAGER).auto_match_and_show():
                new_matches.append(new_match)
            match_result.configure(text='\n'.join([str(match) for match in new_matches]))

        def add_manual_match():
            if len(match_result.cget("text").split("\n")) > 5:
                return
            student_name = combobox_student.get()
            volunteer_name = combobox_volunteer.get()
            if student_name == "Student" or volunteer_name == "Volunteer":
                return
            db_handler = DbHandler()
            student = db_handler.get_student_by_name(student_name)
            student_id = db_handler.get_student_id_by_name(student_name)
            volunteer = db_handler.get_volunteer_by_name(volunteer_name)
            volunteer_id = db_handler.get_volunteer_id_by_name(volunteer_name)
            if not Matcher.check_that_there_is_no_gender_problem(student, volunteer):
                print("Gender problem")
                return
            new_manual_match = Match(student_id, volunteer_id)
            new_matches.append(new_manual_match)
            match_result.configure(text='\n'.join(match_result.cget("text").split("\n") + [str(new_manual_match)]))

            # reset comboboxes
            combobox_student.set("Student")
            combobox_volunteer.set("Volunteer")

        def commit_matches(new_matches):
            DbHandler().add_objects_to_db(new_matches)
            print("Sending introduction emails to new participants, this might take a while...")
            # for match in matches:
            #     match.send_introduction_message()

            # refresh page
            new_matches = []
            match_result.configure(text="")
            self.show_data(type="Match")
            self.show_remove(type="Match")
            self.show_send_email(type="Match")

        new_matches = []

        auto_match_label = customtkinter.CTkLabel(self.left_data_frame, text="Match", font=customtkinter.CTkFont(size=20, weight="bold"))
        auto_match_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        match_method_picker = customtkinter.CTkSegmentedButton(self.left_data_frame, values=["auto", "manual"], command=self.show_match)
        match_method_picker.set(method)
        match_method_picker.grid(row=1, column=0, padx=20, pady=(7,7), sticky="nsew")

        match_result = customtkinter.CTkLabel(self.left_data_frame, text="", height=100, width=180, bg_color="white")
        match_result.grid(row=2, column=0, padx=20, pady=(7,7))

        if match_method_picker.get() == "auto":
            auto_match_button = customtkinter.CTkButton(self.left_data_frame, command=suggest_auto_match, text="Suggest auto match")
            auto_match_button.grid(row=3, column=0, padx=20, pady=10, sticky="s")

        elif match_method_picker.get() == "manual":
            manual_match_picking_frame = customtkinter.CTkFrame(self.left_data_frame)
            manual_match_picking_frame.grid(row=3, column=0)
            
            db_handler = DbHandler()
            combobox_student = customtkinter.CTkComboBox(manual_match_picking_frame, values=["Student"] + db_handler.get_students_names(only_free=True), width=100)
            combobox_student.grid(row=0, column=0, padx=(0, 2))

            combobox_volunteer = customtkinter.CTkComboBox(manual_match_picking_frame, values=["Volunteer"] + db_handler.get_volunteers_names(only_free=True), width=100)
            combobox_volunteer.grid(row=0, column=1, padx=(2, 0))

            add_button = customtkinter.CTkButton(self.left_data_frame, command=add_manual_match, text="Add nominal match")
            add_button.grid(row=4, column=0, padx=20, pady=10, sticky="s")

        submit_button = customtkinter.CTkButton(self.left_data_frame, command=lambda: commit_matches(new_matches), text="Approve")
        submit_button.grid(row=5, column=0, padx=20, pady=10, sticky="s")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    @staticmethod
    def open_mailjet_website():
        url = 'https://app.mailjet.com/'
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
        webbrowser.get(chrome_path).open(url)

if __name__ == "__main__":
    app = App()
    app.mainloop()