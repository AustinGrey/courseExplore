import codecs
import sqlite3 as sql
import os
import re

'''
@TODO
- Seperate out faculties and departments
- Make subject codes the id?
'''

course_filename = "courseDump.txt"
subject_filename = "subjectDump.txt"


# hard coded list of subject codes for some pruning later,
# @TODO build this algorithmically from the subjects
subs_list = [
'ABROD', 'ACCTG', 'AGRMT', 'AREC', 'AFNS', 'ALES', 'ASL', 'ANAT', 'AN SC', 'ANTHR', 'ARAB', 'ART H', 'ART', 'ASTRO', 'AUACC', 'AUART', 'AUBIO', 'AUCHE', 'AUCLA', 'AUCSL', 'AUCSC', 'AUCRI', 'AUDRA', 'AUECO', 'AUEFX', 'AUEDC', 'AUEPS', 'AUEAP', 'AUENG', 'AUENV', 'AUFRE', 'AUGEO', 'AUGER', 'AUGDS', 'AUGRE', 'AUHIS', 'AUIND', 'AUIDS', 'AULAN', 'AULAT', 'AUMGT', 'AUMAT', 'AUMUS', 'AUPHI', 'AUPAC', 'AUPED', 'AUPHY', 'AUPOL', 'AUPSY', 'AUREL', 'AUSCA', 'AUSOC', 'AUSPA', 'AUSTA', 'AULIT', 'BIOCH', 'BIOIN', 'BIOL', 'BME', 'BOT', 'BUEC', 'B LAW', 'BUS', 'CELL', 'CH E', 'CME', 'CHEM', 'CHINA', 'CHRTC', 'CHRTP', 'CIV E', 'CLASS', 'CSD', 'COMM', 'MACE', 'CSL', 'C LIT', 'CMPE', 'CMPUT', 'DAC', 'DANCE', 'D HYG', 'DDS', 'DENT', 'DMED', 'DES', 'DRAMA', 'EAS', 'EASIA', 'ECON', 'EDCT', 'EDES', 'EDEL', 'EDFX', 'EDIT', 'EDPS', 'EDPY', 'EDSE', 'EDU', 'ECE', 'ENG M', 'EN PH', 'ENCMP', 'ENGG', 'EAP', 'ENGL', 'ENT', 'ENV E', 'ENCS', 'EXCH', 'EXT', 'ADMI', 'ANATE', 'ALS', 'ANGL', 'ANTHE', 'ADRAM', 'BIOCM', 'BIOLE', 'CHIM', 'ECONE', 'EDU F', 'EDU M', 'EDU P', 'EDU S', 'ESPA', 'ETCAN', 'ET RE', 'ETIN', 'FRANC', 'HISTE', 'IMINE', 'LINGQ', 'MATHQ', 'M EDU', 'MICRE', 'MUSIQ', 'PHILE', 'PHYSE', 'PHYSQ', 'PSYCE', 'SC PO', 'SCSOC', 'SCSP', 'SOCIE', 'STATQ', 'F MED', 'FS', 'FIN', 'FOREC', 'FREN', 'GSJ', 'GENET', 'GEOPH', 'GERM', 'GREEK', 'HE ED', 'HEBR', 'HINDI', 'HADVC', 'HIST', 'HECOL', 'HGP', 'HRM', 'HUCO', 'IMIN', 'IPG', 'INT D', 'ITAL', 'JAPAN', 'KIN', 'KOREA', 'LABMP', 'LA ST', 'LATIN', 'LAW', 'LIS', 'LING', 'M REG', 'MIS', 'MGTSC', 'MA SC', 'MARK', 'MINT', 'MAT E', 'MA PH', 'MATH', 'MEC E', 'MDGEN', 'MLSCI', 'MMI', 'MED', 'MICRB', 'MEAS', 'MIN E', 'MLCS', 'MM', 'MUSIC', 'NANO', 'NS', 'NEURO', 'NORW', 'NURS', 'NU FS', 'NUTR', 'OB GY', 'OCCTH', 'ONCOL', 'OM', 'OPHTH', 'OBIOL', 'PAED', 'PALEO', 'PERS', 'PET E', 'PMCOL', 'PHARM', 'PHIL', 'PAC', 'PERLS', 'PTHER', 'PHYS', 'PHYSL', 'PL SC', 'POLSH', 'POL S', 'PORT', 'PGDE', 'PGME', 'PSYCI', 'PSYCO', 'PUNJ', 'RADTH', 'RADDI', 'RLS', 'REHAB', 'RELIG', 'REN R', 'RSCH', 'R SOC', 'RUSS', 'SCAND', 'SPH', 'SCI', 'STS', 'SC INF', 'SLAV', 'SOC', 'SPAN', 'STAT', 'SMO', 'SURG', 'SWED', 'T DES', 'THES', 'UKR', 'UNIV', 'PLAN', 'WGS', 'WKEXP', 'WRITE', 'WRS', 'ZOOL'
]

print("Beginning to Parse Class Listings")




# Get the course and subject listings
f = codecs.open(course_filename, encoding='utf-8')
course_file = [line.strip() for line in f]
f = codecs.open(subject_filename, encoding='utf-8')
subjects_file = [line.strip() for line in f]

# Open or create database, then connect cursor
filename = os.path.join(os.path.dirname(__file__), 'database.db3')
conn = sql.connect(filename)
c = conn.cursor()

test_set = set()

prereq_list = []

# Get all of the subjects, then courses, then add them to the database
for i in range(0, len(course_file)):
	if course_file[i][0] == '#':
		#subject start identified, extract, insert
		subject_name = course_file[i+1] # name
		subject_code = course_file[i+2] # code
		subject_dept = course_file[i+3] # offering department
		# a subject can have any number of notes
		subject_notes = []
		j = i+4
		while (not course_file[j].startswith('Undergraduate Courses') 
			and not course_file[j].startswith('Graduate Courses')
			and not course_file[j].startswith('Cours de 1er cycle')
			and not course_file[j].startswith('Cours de 2e cycle')
			and not course_file[j].startswith('#')):
			subject_notes.append(course_file[j])
			j += 1
		
		# Debugger code to view what was scraped
		'''
		print(subject_code + "\t\t" + subject_name + " ---> " + subject_dept)
		for line in subject_notes:
			print("\t\t\t" + line)
		input()
		'''
		
		# Handle department first
		# First check if it already exists
		c.execute('SELECT id FROM departments WHERE name=?', (subject_dept,))
		dept_id = c.fetchone()
		dept_id = dept_id[0] if dept_id != None else None
		# Insert
		c.execute('INSERT OR REPLACE INTO departments (id, name) VALUES (?,?)', (dept_id, subject_dept))
		# Keep track of the id as it now exists in the database
		c.execute('SELECT id FROM departments WHERE name=?', (subject_dept,))
		dept_id = c.fetchone()[0]
		
		# Handle subjects
		# @TODO: if the course code changes, should we create a new subject?
		# First check if it already exists
		c.execute('SELECT id FROM subjects WHERE code=?', (subject_code,))
		subject_id = c.fetchone()
		subject_id = subject_id[0] if subject_id != None else None
		# Insert
		c.execute('INSERT OR REPLACE INTO subjects (id, name, code, offering_dept, notes) VALUES (?,?,?,?,?)', 
			(subject_id, subject_name, subject_code, dept_id, "\n".join(subject_notes)))
		# Keep track of the id as it now exists in the database
		c.execute('SELECT id FROM subjects WHERE code=?', (subject_code,))
		subject_id = c.fetchone()[0]
		
		# scan the sub sections under the subject for course listings,
		# Each subject usually has at least either undergraduate listings, or graduate listings as a section.
		# However, the sections might contain additional notes, department info, and the like
		# Plan: scan down lines, keep of track if you are in the undergrad or grad section
		# any non-class lines are added to the notes for that section
		if (course_file[j].startswith('Undergraduate Courses') or course_file[j].startswith('Cours de 1er cycle')):
			current_heading = "u_grad"
		elif (course_file[j].startswith('Graduate Courses') or course_file[j].startswith('Cours de 2e cycle')):
			current_heading = "grad"
		elif (course_file[j].startswith('#')):
			# This implies the subject has no courses listed, and we are done with it
			print("WARN: No courses for subject " + subject_code + ", skipping.")
			continue
		else:
			print("Unhandled initial " + subject_code + " sub-section prefix: " + course_file[j])
			break
		j += 1 #this subsection header is handled, move on
			
		undergrad_notes = ""
		grad_notes = ""
		
		while (j < len(course_file) and not course_file[j].startswith('#')):
			line_code = course_file[j][0:len(subject_code)]
			if line_code != subject_code:
				#possibly a new section, or notes
				if (course_file[j].startswith('Undergraduate Courses') or course_file[j].startswith('Cours de 1er cycle')):
					current_heading = "u_grad"
				elif (course_file[j].startswith('Graduate Courses') or course_file[j].startswith('Cours de 2e cycle')):
					current_heading = "grad"
				else:
					#notes, add to the notes section
					if current_heading == "u_grad": 
						undergrad_notes += course_file[j] + "\n"
					elif current_heading == "grad":
						grad_notes += course_file[j] + "\n"
			else:
				# this is a class -> parse the class details and add to database
				
				# consistency check the line, every class should list it's credits, if not this might not be a class
				if ("Œ" not in course_file[j]):
					print("consistency error line " + str(j+1) + ": possibly not a class listing, could not find credit score")
					print("                            " + course_file[j])
					break
				
				line = course_file[j]
				# definitely a class listing
				
				# remove the subject code prefix and space
				line = line[len(subject_code)+1:]
				
				# extract 3 digit course number
				course_num = line[0:3] 
				line = line[3:]
				
				# clean line from phrases that interfere with regex
				if "e.g." in line: line = line.replace("e.g.", "eg")
				if "i.e." in line: line = line.replace("i.e.", "ie")
				
				# extract the prerequisites statement
				match = re.search("Prerequisites?:[^.]*\.", line)
				if match:
					prereq_string = match.group(0)
					line = line.replace(prereq_string, "")
					prereq_string = prereq_string.replace("Prerequisite: ", "")
					prereq_string = prereq_string.replace("Prerequisites: ", "")
				else:
					prereq_string = None
				
				# extract the corequsites statement
				match = re.search("[^.]*Corequisites?:[^.]*\.", line)
				if match:
					coreq_string = match.group(0)
					line = line.replace(coreq_string, "")
				else:
					coreq_string = None
					
				# extract the credit number
				match = re.search("Œ[0-9.-]*", line)
				if match:
					credit_string = match.group(0)
					line = line.replace(credit_string, "") # remove the string from the line, then clean it up
					credit_string = credit_string.replace("(", "")
					credit_string = credit_string.replace(")", "")
					credit_string = credit_string.replace("Œ", "")
				else:
					print("FATAL ERR: No credit amount found for line " + str(j+1) + " when one was expected")
					break
					
				# extract the fee index
				match = re.search("\(fi[^(]*\)|(\(variable\))", line)
				if match:
					fi_string = match.group(0)
					line = line.replace(fi_string, "")
					fi_string = fi_string.replace("(", "")
					fi_string = fi_string.replace(")", "")
					fi_string = fi_string.replace("fi", "")
					fi_string.strip()
				else:
					print("ERR: No fee index found for line " + str(j+1) + " when one was expected")
				
				# extract the open limited and open key phrases, order here matters between these two
				match = re.search("=OPEN-LIMITED", line)
				if match:
					open_limited = True
					line = line.replace("=OPEN-LIMITED", "")
				else:
					open_limited = False
					
				match = re.search("=OPEN", line)
				if match:
					open = True
					line = line.replace("=OPEN", "")
				else:
					open = False
				
				# extract the course name
				# regex looks for all characters before the first left parenthesis, there are some exceptions for classes
				# that have the bad habit of parenthesising their long names
				# @TODO seems like there are too many exceptions to be sustainable for a future usage of the tool, is there another way to detect the name?
				match = re.search("^[^(]*(\(CALL\)|\(TESL\)|\(bhakti\)|\(Track and Field\)|\(#1\)|\(#2\)|\(1600-1815\)|\(Ages 5 - 12\)|\(Canada\)|\(Capstone Course\)|\(Chant\)|\(Classical\)|\(Cornerstone Course\)|\(Course Based Masters\)|\(Course-based Masters\)|\(Cuba\)|\(Dental\)|\(Enriched\)|\(Fast Pitch\)|\(For Further Study\)|\(Greece\)|\(Hellenistic\)|\(MEMS\)|\(MEMS\/NEMS\)|\(Mechanics\)|\(Migration and Identity\)|\(Post\)|\(Printemps\/Eté, 0-3L-0\)|\(Re\)|\(Wave Motion, Sound, Heat, and Optics\)|\(ou la chimie durable\)|\(s\))?[^(]*", line)
				if match:
					name_string = match.group(0)
					line = line.replace(name_string, "")
				else:
					print("ERR: No case name found for line " + str(j+1) + " when one was expected")
					
				# extract the time commitment string
				match = re.search("^\([^\)]*\)", line)
				if match:
					times_string = match.group(0)
					line = line.replace(times_string, "")
				else:
					print("ERR: No time commitment string found for line " + str(j+1) + " when one was expected")
				
				# usually this leaves a period and leading space in front of the notes, remove them
				if line[0:2] == ". ": line = line[2:]
				
				# add the class to the database
				# first check if it already exists
				c.execute('SELECT id FROM courses WHERE subject=? and number=?', (subject_id,course_num))
				course_id = c.fetchone()
				course_id = course_id[0] if course_id != None else None
				# Insert
				c.execute('''
				INSERT OR REPLACE INTO courses 
				(id, subject, number, credits, fi, open_study, open_study_limited, is_undergrad, is_grad) 
				VALUES (?,?,?,?,?,?,?,?,?)''', 
				(course_id, subject_id, course_num, 
				credit_string, fi_string, open, open_limited, 
				True if current_heading == "u_grad" else False,
				True if current_heading == "grad" else False,))
				
				
				# parse the pre and co reqs, add to a list that will be added to the database later,
				# after all the classes themselves are added, to avoid foreign key constraint issues.
				
				# expand the prereqs string, 'naked' numbers should recieve their course code
				# e.g. 				'MATH 114 or 115, SCI 133, 156, and 167.'
				# should become 	'MATH 114 or MATH 115, SCI 133, SCI 156, and SCI 167.'
				# Lazy and bad solution
				# 1. Get a list of all 3 digit numbers in the string
				# 2. Get a list of all the subject codes in the string
				# 3. Iterate over the course numbers, and match it with the closest preceeding subject code
				
				if (prereq_string is not None):
					# extract the numbers codes, and the subject codes
					num_matches = re.finditer("[0-9]{3}", prereq_string)
					sub_matches = re.finditer("(ABROD|ACCTG|AGRMT|AREC|AFNS|ALES|ASL|ANAT|AN SC|ANTHR|ARAB|ART H|ART|ASTRO|AUACC|AUART|AUBIO|AUCHE|AUCLA|AUCSL|AUCSC|AUCRI|AUDRA|AUECO|AUEFX|AUEDC|AUEPS|AUEAP|AUENG|AUENV|AUFRE|AUGEO|AUGER|AUGDS|AUGRE|AUHIS|AUIND|AUIDS|AULAN|AULAT|AUMGT|AUMAT|AUMUS|AUPHI|AUPAC|AUPED|AUPHY|AUPOL|AUPSY|AUREL|AUSCA|AUSOC|AUSPA|AUSTA|AULIT|BIOCH|BIOIN|BIOL|BME|BOT|BUEC|B LAW|BUS|CELL|CH E|CME|CHEM|CHINA|CHRTC|CHRTP|CIV E|CLASS|CSD|COMM|MACE|CSL|C LIT|CMPE|CMPUT|DAC|DANCE|D HYG|DDS|DENT|DMED|DES|DRAMA|EAS|EASIA|ECON|EDCT|EDES|EDEL|EDFX|EDIT|EDPS|EDPY|EDSE|EDU|ECE|ENG M|EN PH|ENCMP|ENGG|EAP|ENGL|ENT|ENV E|ENCS|EXCH|EXT|ADMI|ANATE|ALS|ANGL|ANTHE|ADRAM|BIOCM|BIOLE|CHIM|ECONE|EDU F|EDU M|EDU P|EDU S|ESPA|ETCAN|ET RE|ETIN|FRANC|HISTE|IMINE|LINGQ|MATHQ|M EDU|MICRE|MUSIQ|PHILE|PHYSE|PHYSQ|PSYCE|SC PO|SCSOC|SCSP|SOCIE|STATQ|F MED|FS|FIN|FOREC|FREN|GSJ|GENET|GEOPH|GERM|GREEK|HE ED|HEBR|HINDI|HADVC|HIST|HECOL|HGP|HRM|HUCO|IMIN|IPG|INT D|ITAL|JAPAN|KIN|KOREA|LABMP|LA ST|LATIN|LAW|LIS|LING|M REG|MIS|MGTSC|MA SC|MARK|MINT|MAT E|MA PH|MATH|MEC E|MDGEN|MLSCI|MMI|MED|MICRB|MEAS|MIN E|MLCS|MM|MUSIC|NANO|NS|NEURO|NORW|NURS|NU FS|NUTR|OB GY|OCCTH|ONCOL|OM|OPHTH|OBIOL|PAED|PALEO|PERS|PET E|PMCOL|PHARM|PHIL|PAC|PERLS|PTHER|PHYS|PHYSL|PL SC|POLSH|POL S|PORT|PGDE|PGME|PSYCI|PSYCO|PUNJ|RADTH|RADDI|RLS|REHAB|RELIG|REN R|RSCH|R SOC|RUSS|SCAND|SPH|SCI|STS|SC INF|SLAV|SOC|SPAN|STAT|SMO|SURG|SWED|T DES|THES|UKR|UNIV|PLAN|WGS|WKEXP|WRITE|WRS|ZOOL)", prereq_string)
					
					num_list = [(match, match.start()) for match in num_matches]
					sub_list = [(match, match.start()) for match in sub_matches]
					
					num = 0
					sub = 0
					while(num < len(num_list) and sub < len(sub_list)):
						num += 1
						sub += 1
				###################FIGURE FROM HERE
				
				
				
				
				
			j += 1

			
test_list = list(test_set)
test_list.sort()
for line in test_list:
	print(line)
	
	
conn.commit()