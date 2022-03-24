from email import message
from grpc import server
import GetGrade, json
import smtplib
from email.message import EmailMessage
import Config

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

compressed = True
q = GetGrade.Collect_Data(True)
if compressed:
	message = ""
	for i in q:
		#print(i)
		message += f"{i['Course']}: {i['Grade']}\n"
	send_email("FOCUS", message, Config.Email_Send)
else:
	send_email("FOCUS", str(q), Config.Email_Send)