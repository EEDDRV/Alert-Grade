import pandas, sys, json
import time, Config
import requests, os
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
start_time = time.time()

class Course:
	def __init__(self, Peroid, Course, Teacher, Ex, Unx, Tardy, Grade, Assignments = []):
		self.Peroid = Peroid
		self.Course = Course
		self.Teacher = Teacher
		self.Ex = Ex
		self.Unx = Unx
		self.Tardy = Tardy
		self.Grade = Grade
		self.Assignments = Assignments
	def __ToJson__(self):
		return {
			"Course": self.Course,
			"Peroid": self.Peroid,
			"Teacher": self.Teacher,
			"Ex": self.Ex,
			"Unx": self.Unx,
			"Tardy": self.Tardy,
			"Grade": self.Grade,
			"Assignments": self.Assignments
		}
class Assignment:
	def __init__(self, Assignment = "N/A", Points_Earned = "N/A",
	 Precent = "N/A", Grade = "N/A", Commet = "N/A", Assigned = "N/A", Due = "N/A",
	  Last_Modified = "N/A", Category = "N/A", Resources = "N/A",
	  Last_Upload_Date = "N/A", Submit_Files = "N/A"):
		self.Assignment = Assignment
		self.Points_Earned = Points_Earned
		self.Precent = Precent
		self.Grade = Grade
		self.Commet = Commet
		self.Assigned = Assigned
		self.Due = Due
		self.Last_Modified = Last_Modified
		self.Category = Category
		self.Resources = Resources
		self.Last_Upload_Date = Last_Upload_Date
		self.Submit_Files = Submit_Files
	def __ToJson__(self):
		return {
			"Assignment": self.Assignment,
			"Points_Earned": self.Points_Earned,
			"Precent": self.Precent,
			"Grade": self.Grade,
			"Commet": self.Commet,
			"Assigned": self.Assigned,
			"Due": self.Due,
			"Last_Modified": self.Last_Modified,
			"Category": self.Category,
			"Resources": self.Resources,
			"Last_Upload_Date": self.Last_Upload_Date,
			"Submit_Files": self.Submit_Files
		}

def Collect_Assignments(driver):
	Assignments = []
	try:
		WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, "grades-grid")))
	except:
		pass
	
	if driver.find_elements_by_partial_link_text("No Assignments Found"):
		return Assignments	
	
	table = driver.find_element_by_class_name("grades-grid")
	#print(f'##{table.find_elements_by_tag_name("tr")[1].text }##')
	for row in table.find_elements_by_tag_name("tr"):
		if row.text == "Assignment Points Earned Grade Comment Assigned Due Last Modified Category Resources Last Upload Date Submit Files":
			pass
		if row.text == "":
			pass
		cell = row.find_elements_by_tag_name("td")
		#for r, i in enumerate(cell):
		#	print(f"{i.text}-{r}\n----")
		#print("|||")
		try:
			if table.find_elements_by_tag_name("tr")[1].text == "Assignment Points Earned Grade Comment Assigned Due Last Modified Category Resources Last Upload Date Submit Files":
				grade = Assignment(Assignment = cell[1].text,
				Points_Earned = cell[2].text,
				Grade = cell[3].text,
				Commet = cell[4].text,
				Assigned = cell[5].text,
				Due = cell[6].text,
				Last_Modified = cell[7].text,
				Category = cell[8].text,
				Resources = cell[9].text,
				Last_Upload_Date = cell[10].text,
				Submit_Files = cell[11].text
				)
			else:
				grade = Assignment(Assignment = cell[1].text,
				Points_Earned = cell[2].text,
				Precent = cell[3].text,
				Grade = cell[4].text,
				Commet = cell[5].text,
				Assigned = cell[6].text,
				Due = cell[7].text,
				Last_Modified = cell[8].text,
				Category = cell[9].text,
				Resources = cell[10].text,
				Last_Upload_Date = cell[11].text,
				Submit_Files = cell[12].text
				)
			if grade.Assignment == "N/A" or grade.Assignment == "":
				pass
			else:
				Assignments.append(grade)
		except:
			pass
			#print(f"++{row.text}++")
			#for i in cell:
			#	print(f"~~{i.text}~~")
	return Assignments

def Collect_Data(Grades_only = True, show = False):
	chrome_options = Options()
	if show == True:
		chrome_options.headless = True
		chrome_options.add_argument('--log-level=3')
	driver = webdriver.Chrome(executable_path=Config.PATH, chrome_options=chrome_options)
	sys.stdout.write("\033[F") #back to previous line
	sys.stdout.write("\033[K") #clear line
	sys.stdout.write("\033[F") #back to previous line
	sys.stdout.write("\033[K") #clear line
	driver.get("https://duval.focusschoolsoftware.com/focus/")
	email = Config.Email
	password = Config.Password
	driver.execute_script("HRD.selection('AD AUTHORITY');");
	driver.find_element_by_id("userNameInput").send_keys(email)
	driver.find_element_by_id("passwordInput").send_keys(password)
	driver.execute_script("Login.submitLoginRequest();");
	table = driver.find_element_by_class_name("grades-table-classes")
	Courses = []
	for row in table.find_elements_by_tag_name("tr"):
		cell = row.find_elements_by_tag_name("td")
		Courses.append(Course(cell[2].text, cell[5].text, cell[6].text,
		cell[8].text, cell[9].text, cell[10].text, cell[12].text))
		#print(', '.join("%s: %s" % item for item in vars(course).items())) # <-- this line is for testing
	qq = json.loads("""[]""")
	if Grades_only != True:
		#print(len(Courses))
		for i in range(len(Courses)):
			e = WebDriverWait(driver, 1).until(
				EC.element_to_be_clickable((By.CLASS_NAME, "grades-table-classes")))
			driver.find_element_by_class_name("grades-table-classes").find_elements_by_tag_name("tr")[i].find_elements_by_tag_name("td")[12].click()
			result = Collect_Assignments(driver)
			qqq = []
			for ii in result:
				qqq.append(ii.__ToJson__())
			driver.back()
			Courses[i].Assignments = qqq
			qq.append(Courses[i].__ToJson__())
	else:
		for i in range(len(Courses)):
			qq.append(Courses[i].__ToJson__())

	driver.quit()
	return qq

if __name__ == "__main__":
	start_time = time.time()
	qq = Collect_Data(Grades_only = True)
	with open('ee.json', 'w+') as outfile:
		json.dump(obj=qq, fp=outfile, indent=4)
	print("--- %s seconds ---" % (time.time() - start_time))
