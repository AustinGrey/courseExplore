import codecs
import sqlite3 as sql
import os

'''
@TODO
- Seperate out faculties and departments
- Make subject codes the id?
'''

course_filename = "courseDump.txt"
subject_filename = "subjectDump.txt"


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
				course_num = line[0:3] #course number is 3 digits
				line = line[3:]
				
				
			j += 1
		
		
		# This old version couldn't handle the potential notes and sub section headings, but it could
		# handle checking for poorly formatted input where pre-reqs were accidently listed as classes for a subject
		'''
		undergrad_notes = ""
		if (course_file[j].startswith('Undergraduate Courses') 
			or course_file[j].startswith('Cours de 1er cycle')):
			j += 1
			note_scanning = True
			# Get Undergrad Courses, continue where we left off scanning notes
			while (not course_file[j].startswith('Graduate Courses')
				and not course_file[j].startswith('Cours de 2e cycle')
				and not course_file[j].startswith('#')):
				
				line_code = course_file[j][0:len(subject_code)]
				
				# Common error, a note or other sentence starting with a course code is on the wrong line
				# Check for course code consistency
				# @TODO there is a bug here, if an incorrect course code is right after the notes, it will be included in the notes
				if line_code != subject_code:
					if note_scanning:
						undergrad_notes += course_file[j]
						j = j+1
						continue
					print("consistency error line " + str(j+1) + ": Subject " + subject_code + " has line with code " + line_code)
					break
				else:
					note_scanning = False
				j += 1
		'''


conn.commit()