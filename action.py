import json
from db import DB
from process import Process

mydb    = DB()

myprocess   = Process()

print("Masukkan komentar yang akan diproses")
value   = input()

print(json.dumps(mydb.validateWords(value, None)))