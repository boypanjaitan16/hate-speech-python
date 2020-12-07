import pandas as pd
from db import DB
from styleframe import StyleFrame, Styler, utils
import sys

mydb        = DB()

try:
    table       = pd.read_excel("resources/data-to-compare.xlsx")
except:
    print("file data-to-compare.xlsx tidak ditemukan di direktori resources")
    sys.exit(1)

ratePakar   = table['Termasuk Komentar']
komentars   = table['Komentar']
namas       = table['Nama']

results     = []

for i,val in enumerate(komentars):
    results.append(mydb.validateWords(val, namas[i]))

fix     = {
    'nama'      : [],
    'komentar'  : [],
    'ulasan_prediksi'   : [],
    'ulasan_aktual'     : []
}  # dictionaries

compareVal  = {
    'tp'    : 0,
    'fn'    : 0,
    'tn'    : 0,
    'fp'    : 0
}

for i,data in enumerate(results):
    if data['hasil'].lower() == 'positif' and ratePakar[i] == 'positif':
        compareVal['tp'] += 1
    if data['hasil'].lower() == 'positif' and ratePakar[i] == 'negatif':
        compareVal['fn'] += 1
    if data['hasil'].lower() == 'negatif' and ratePakar[i] == 'positif':
        compareVal['fp'] += 1
    if data['hasil'].lower() == 'negatif' and ratePakar[i] == 'negatif':
        compareVal['tn'] += 1

    nama 	= fix['nama']
    nama.append(data['nama'])
    fix['nama']	= nama

    komentar = fix['komentar']
    komentar.append(data['komentar'])
    fix['komentar'] = komentar

    prediksi = fix['ulasan_prediksi']
    prediksi.append(data['hasil'].lower())
    fix['ulasan_prediksi'] = prediksi

    aktual = fix['ulasan_aktual']
    aktual.append(ratePakar[i])
    fix['ulasan_aktual'] = aktual


outputFile = 'output/compare-output.xlsx'

df      = pd.DataFrame(fix)
sf      = StyleFrame(df)
for col_name in df.columns:
    sf.apply_style_by_indexes(indexes_to_style=sf[(sf['ulasan_prediksi'] == 'positif') & (sf['ulasan_aktual'] == 'positif')], cols_to_style=['ulasan_prediksi','ulasan_aktual'], styler_obj=Styler(bg_color=utils.colors.green))
    sf.apply_style_by_indexes(indexes_to_style=sf[(sf['ulasan_prediksi'] == 'positif') & (sf['ulasan_aktual'] == 'negatif')], cols_to_style=['ulasan_prediksi','ulasan_aktual'], styler_obj=Styler(bg_color=utils.colors.blue))
    sf.apply_style_by_indexes(indexes_to_style=sf[(sf['ulasan_prediksi'] == 'negatif') & (sf['ulasan_aktual'] == 'positif')], cols_to_style=['ulasan_prediksi','ulasan_aktual'], styler_obj=Styler(bg_color=utils.colors.yellow))
    sf.apply_style_by_indexes(indexes_to_style=sf[(sf['ulasan_prediksi'] == 'negatif') & (sf['ulasan_aktual'] == 'negatif')], cols_to_style=['ulasan_prediksi','ulasan_aktual'], styler_obj=Styler(bg_color=utils.colors.red))
# sf.to_csv('Hasil-compare.csv').save()
sf.to_excel(outputFile).save()

accuracy    = (compareVal['tp'] + compareVal['tn']) / (compareVal['tp'] + compareVal['tn'] + compareVal['fp'] + compareVal['fn'])
precission  = compareVal['tp'] / (compareVal['tp'] + compareVal['fp']) if (compareVal['tp'] + compareVal['fp']) > 0 else 0
recall      = compareVal['tp'] / (compareVal['tp'] + compareVal['fn']) if (compareVal['tp'] + compareVal['fn']) > 0 else 0
fMeasure    = (2*precission*recall)/(precission+recall) if (precission+recall) > 0 else 0

print('Pembandingan berhasil, hasil pembandingan disimpan dalam file '+outputFile)
print('')
print('TP : '+str(compareVal['tp']))
print('TN : '+str(compareVal['tn']))
print('FP : '+str(compareVal['fp']))
print('FN : '+str(compareVal['fn']))
print('')
print('Accuracy : '+str(accuracy))
print('Precission : '+str(precission))
print('Recall : '+str(recall))
print('F-Measure : '+str(fMeasure))