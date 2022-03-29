import API, Config, time, sys, json
from email import message
import smtplib
from email.message import EmailMessage

def send_email(subject, body, to):
	msg = EmailMessage()
	msg.set_content(body)
	msg['subject'] = subject
	msg['to'] = to
	user = Config.Send_Email
	msg['from'] = user
	password = Config.Send_Email_Password
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(user, password)
	server.send_message(msg)
	server.quit()

if __name__ == "__main__":
	Original_Information = API.Get_Grades(Config.Email, Config.Password)

	while True:
		New_Information = API.Get_Grades(Config.Email, Config.Password)
		Courses_Information_Only = New_Information["initial_contexts"]["PortalController"]["data"]["enrollments"][0]["grades"]["rows"]
		Courses_Information = {}
		for i in Courses_Information_Only:
			Courses_Information.update({i["course_name"]: i["calculated_grade"]})
		if Courses_Information != Original_Information:
			Original_Information = Courses_Information
			sms_message = ""
			for i in Courses_Information:
				sms_message += f"{i}: {Courses_Information[i]}\n"
			sms_message += f"Time sent from server: {time.strftime('%H:%M:%S')}"
			send_email("FOCUS", sms_message, Config.Email_Send)
			print("[*] Message sent!")
#	with open('q.json', 'w') as f:
#		json.dump(Courses_Information, f, indent=4, sort_keys=True)