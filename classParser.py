import codecs
import sqlite3 as sql
import os

f_name = "testcourse2.txt"

f = codecs.open(f_name, encoding='utf-8')

print("Beginning to Parse Class Listings")

contents = [line for line in f]

#Open or create database
filename = os.path.join(os.path.dirname(__file__), 'database.db')
conn = sql.connect(filename)
c = conn.cursor()

print(contents[0])


