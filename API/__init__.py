from unittest import result
from pytest import Session
import requests, json, re, time, Config
from bs4 import BeautifulSoup as BS

def Get_Grades(UserName, Password):
	headers = {}
	Login_data = {
		'UserName': UserName,
		'Password': Password}
	session = requests.Session()
	# Get SAMLRequest and RelayState
	response = session.get('https://duval.focusschoolsoftware.com/focus/Modules.php?modname=misc/Portal.php', headers=headers)
	doc = BS(response.content, 'html.parser')
	SAMLRequest_and_RelayState = {
		doc.input.attrs["name"]: doc.input.attrs["value"],
		doc.find_all('input')[1].attrs["name"]: doc.find_all('input')[1].attrs["value"]
	}
	# RESPONSE 2 CONTAINS "MSISSamlRequest", "MSISSamlRequest1", "MSISSamlRequest2", AND "MSISSamlRequest3"
	response2 = session.post('https://fs.duvalschools.org/adfs/ls/', headers=headers, data=SAMLRequest_and_RelayState)
	ID_for_session = BS(response2.content, 'html.parser').form.attrs["action"].split("=")[1]
	# This gets the new SAMLRequest and RelayState
	response3 = session.post(f'https://fs.duvalschools.org/adfs/ls/?client-request-id={ID_for_session}&RedirectToIdentityProvider=AD+AUTHORITY',
		headers=headers, data=Login_data, cookies=response2.cookies)
	doc = BS(response3.content, 'html.parser')
	SAMLRequest_and_RelayState = {
		doc.input.attrs["name"]: doc.input.attrs["value"],
		doc.find_all('input')[1].attrs["name"]: doc.find_all('input')[1].attrs["value"]
	}
	# This gets the new "PHPSESSID" cookie
	response4 = session.post('https://duval.focusschoolsoftware.com/focus/sso/saml2/acs.php',
		headers=headers, params={'id': 'saml'}, cookies=response.cookies.get_dict(), data=SAMLRequest_and_RelayState)
	# This gets the Gradebook from the main page
	response5 = requests.get('https://duval.focusschoolsoftware.com/focus/Modules.php',
	headers=headers, cookies={"PHPSESSID": response4.cookies.get_dict()["PHPSESSID"]})
	return json.loads((re.search('{"methods[A-z\W_0-9]+}}};', str(response5.text))[0])[:-1])

# Now create a function that gets all the assignments and grades
def Get_All_Assignments(UserName, Password):
	headers = {}
	Login_data = {
		'UserName': UserName,
		'Password': Password}
	session = requests.Session()
	# Get SAMLRequest and RelayState
	response = session.get('https://duval.focusschoolsoftware.com/focus/Modules.php?modname=misc/Portal.php', headers=headers)
	doc = BS(response.content, 'html.parser')
	SAMLRequest_and_RelayState = {
		doc.input.attrs["name"]: doc.input.attrs["value"],
		doc.find_all('input')[1].attrs["name"]: doc.find_all('input')[1].attrs["value"]
	}
	# RESPONSE 2 CONTAINS "MSISSamlRequest", "MSISSamlRequest1", "MSISSamlRequest2", AND "MSISSamlRequest3"
	response2 = session.post('https://fs.duvalschools.org/adfs/ls/', headers=headers, data=SAMLRequest_and_RelayState)
	ID_for_session = BS(response2.content, 'html.parser').form.attrs["action"].split("=")[1]
	# This gets the new SAMLRequest and RelayState
	response3 = session.post(f'https://fs.duvalschools.org/adfs/ls/?client-request-id={ID_for_session}&RedirectToIdentityProvider=AD+AUTHORITY',
		headers=headers, data=Login_data, cookies=response2.cookies)
	doc = BS(response3.content, 'html.parser')
	SAMLRequest_and_RelayState = {
		doc.input.attrs["name"]: doc.input.attrs["value"],
		doc.find_all('input')[1].attrs["name"]: doc.find_all('input')[1].attrs["value"]
	}
	# This gets the new "PHPSESSID" cookie
	response4 = session.post('https://duval.focusschoolsoftware.com/focus/sso/saml2/acs.php',
		headers=headers, params={'id': 'saml'}, cookies=response.cookies.get_dict(), data=SAMLRequest_and_RelayState)
	# This gets the Gradebook from the main page
	response5 = requests.get('https://duval.focusschoolsoftware.com/focus/Modules.php',
	headers=headers, cookies={"PHPSESSID": response4.cookies.get_dict()["PHPSESSID"]})
	Grade_Information = json.loads((re.search('{"methods[A-z\W_0-9]+}}};', str(response5.text))[0])[:-1])
	# Collect all the href for each course
	hrefs = []
	Current_Quarter = Grade_Information["initial_contexts"]["PortalController"]["data"]["enrollments"][0]["grades"]["mps"][0]["key"]
	for i in Grade_Information["initial_contexts"]["PortalController"]["data"]["enrollments"][0]["grades"]["rows"]:
		#print(i[Current_Quarter+"_mp_grade_href"])
		hrefs.append(i[Current_Quarter+"_mp_grade_href"])
	# Now get all the assignments for each course
	Assignments = []
	for i in hrefs:
		Assignments.append(Get_Assignments_Internel(i, {"PHPSESSID": response4.cookies.get_dict()["PHPSESSID"]}))
	return [Grade_Information, Assignments]

def Get_Assignments_Internel(url, cookies):
	Course_period_id = re.findall("course_period_id=[0-9]+", url)[0].split("=")[1]
	result1 = requests.get(url, headers={}, cookies=cookies)
	Session_id = (re.findall('"[A-z0-9+=/]+', re.findall('session_id.*\n.*";', result1.text)[0])[0])[1:]
	Call = str({"requests":[{"controller":"StudentGBGradesController","method":"getGradebookGrid","args":[int(Course_period_id)]}]}).replace(' ', '').replace("'", '"')
	headers = {
		'authorization': 'Bearer ' + Session_id,
		'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryaaaaaaaaaaaaaaaa',
	}
	Token = re.findall('token = "([A-Za-z0-9_\./\\-]*)"', result1.text)[1]
	data = '------WebKitFormBoundaryaaaaaaaaaaaaaaaa\r\nContent-Disposition: form-data; name="course_period_id"\r\n\r\n'+Course_period_id+'\r\n------WebKitFormBoundaryaaaaaaaaaaaaaaaa\r\nContent-Disposition: form-data; name="__call__"\r\n\r\n'+Call+'\r\n------WebKitFormBoundaryaaaaaaaaaaaaaaaa\r\nContent-Disposition: form-data; name="__token__"\r\n\r\n'+Token+'\r\n------WebKitFormBoundaryaaaaaaaaaaaaaaaa--\r\n'
	result2 = requests.post('https://duval.focusschoolsoftware.com/focus/classes/FocusModule.class.php',
		headers=headers, cookies=cookies, data=data)
	#print(result2.text)
	return result2