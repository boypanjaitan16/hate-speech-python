from db import DB
import pandas as pd
import json
import sys

try:
    table       = pd.read_excel("resources/data-to-proceed.xlsx")
except:
    print("file data-to-proceed.xlsx tidak ditemukan pada direktori resources/")
    sys.exit(1)

mydb        = DB()
komentars   = table['Komentar']
namas       = table['Nama']
results     = []

for i,val in enumerate(komentars):
    results.append(mydb.validateWords(val, namas[i]))

fix     = {
    'nama'      : [],
    'komentar'  : [],
    'termasuk_komentar' : []
}  # dictionaries

for data in results:
    # print(data)
    nama 	= fix['nama']
    nama.append(data['nama'])
    fix['nama']	= nama

    komentar = fix['komentar']
    komentar.append(data['komentar'])
    fix['komentar'] = komentar

    hasil = fix['termasuk_komentar']
    hasil.append(data['hasil'])
    fix['termasuk_komentar'] = hasil


a       = pd.DataFrame(fix)

outputFile = 'output/process-output.xlsx'
writer = pd.ExcelWriter(outputFile, engine='xlsxwriter')
a.to_excel(writer, sheet_name='Sheet1')
writer.save()

print('penilaian berhasil, disimpan dalam file '+outputFile)
