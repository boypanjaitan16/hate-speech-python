import re
import pandas as pd
import json
import math
import sys

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

class Process:
    fileInput   = "resources/data-to-learn.xlsx"
    fileOutput  = "output/learning-output.xlsx"

    katabuang   = []

    def __init__(self):
        try:
            self.table = pd.read_excel(self.fileInput)
        except:
            print('file data-to-learn.xlsx tidak ditemukan pada direktori resources/')
            sys.exit(1)

        try:
            self.katabuang   = open("resources/stopword.txt")
        except:
            print('file stopword.txt tidak ditemukan pada direktori resources/')
            sys.exit(1)
        
        self.katabuang   = self.katabuang.read()
        self.katabuang   = self.katabuang.split("\n")

    def totalRows(self):
        return self.table.shape[0]

    def cleanComment(self, val):
        value = re.sub(r'\d+', "", str(val))
        value = re.sub(r'\W+', " ", value)
        value = value.lower()

        arrs        = value.split(" ")

        factory     = StemmerFactory()
        stemmer     = factory.create_stemmer()

        for v in arrs:
            if v == '':
                arrs.remove(v)

        narrs = []

        for v in arrs:
            if v not in self.katabuang:
                narrs.append(stemmer.stem(v))

        return narrs

    def getWords(self):
        types       = self.table['Termasuk Komentar']
        komentars   = self.table['Komentar']
        cleans      = []

        for i, val in enumerate(komentars):
            narrs   = self.cleanComment(val)

            cleans.append({'term': narrs, 'type': types[i]})

        return cleans

    def getClasses(self):
        types   = self.table['Termasuk Komentar']
        result  = {'positif': [], 'negatif': []}

        for index, item in enumerate(types):
            if item == 'positif':
                result['positif'].append(index)
            else:
                result['negatif'].append(index)

        return result

    def composeData(self):
        words   = self.getWords()
        result  = {}

        for index, val in enumerate(words):
            for v in val['term']:
                if v in result:
                    excArray = result[v]['posisi']
                    p = "D" + str(index + 1)

                    if p not in excArray:
                        excArray.append(p)

                    negatif = result[v]['negatif']['total']
                    positif = result[v]['positif']['total']
                    arrPos = result[v]['positif']['posisi']
                    arrNeg = result[v]['negatif']['posisi']
                    dfNegatif   = result[v]['negatif']['df']
                    dfPositif   = result[v]['positif']['df']

                    if val['type'] == 'negatif':
                        negatif += 1
                        if p not in arrNeg:
                            arrNeg.append(p)
                            dfNegatif += 1
                    else:
                        positif += 1
                        if p not in arrPos:
                            arrPos.append(p)
                            dfPositif += 1

                    result[v] = {
                        'term'	: v,
                        'total'		: 1 + result[v]['total'],
                        'posisi'	: excArray,
                        'negatif': {
                            'df'        : dfNegatif,
                            'total' 	: negatif,
                            'posisi' 	: arrNeg
                        },
                        'positif': {
                            'df'        : dfPositif,
                            'total'		: positif,
                            'posisi'	: arrPos
                        }
                    }
                else:
                    negatif	= 0
                    positif	= 0
                    arrPos	= []
                    arrNeg	= []
                    dfNegatif   = 0
                    dfPositif   = 0

                    if val['type'] == 'negatif':
                        negatif += 1
                        dfNegatif += 1
                        var  = "D " +str(index +1)
                        arrNeg.append(var)

                    else:
                        positif += 1
                        dfPositif += 1
                        var  = "D " +str(index +1)
                        arrPos.append(var)

                    result[v] = {
                        'term': v,
                        'total': 1,
                        'posisi': ["D " +str(index + 1)],
                        'negatif': {
                            'df'        : dfNegatif,
                            'total' 	: negatif,
                            'posisi' 	: arrNeg
                        },
                        'positif': {
                            'df'        : dfPositif,
                            'total'		: positif,
                            'posisi'	: arrPos
                        }
                    }

        return result

    def cleanLog2(self, atas, bawah):
        if bawah == 0:
            return 0

        if (atas/bawah) <= 0:
            return 0

        return math.log2(atas/bawah)


    def composeMI(self):
        data    = self.composeData()
        rows    = self.totalRows()
        classes = self.getClasses()

        pPos = len(classes['positif']) / rows
        pNeg = len(classes['negatif']) / rows

        for item in data:
            p1t = len(data[item]['posisi']) / rows
            p1_pos = len(data[item]['positif']['posisi']) / rows
            p1_neg = len(data[item]['negatif']['posisi']) / rows

            p0t = (rows - len(data[item]['posisi'])) / rows
            p0_pos = (len(classes['positif']) - len(data[item]['positif']['posisi'])) / rows
            p0_neg = (len(classes['negatif']) - len(data[item]['negatif']['posisi'])) / rows

            logPos1 = math.log2(p1_pos / (p1t * pPos)) if p1_pos / (p1t * pPos) > 0 else 0
            logNeg1 = math.log2(p1_neg / (p1t * pNeg)) if p1_neg / (p1t * pNeg) > 0 else 0
            logPos0 = math.log2(p0_pos / (p0t * pPos)) if p0_pos / (p0t * pPos) > 0 else 0
            logNeg0 = math.log2(p0_neg / (p0t * pNeg)) if p0_neg / (p0t * pNeg) > 0 else 0

            mi = (p1_pos * logPos1) + (p1_neg * logNeg1) + (p0_pos * logPos0) + (p0_neg * logNeg0)

            # data[item]['mi_value']  = mi
            data[item]['mi']        = {
                'value': mi,
                'p1': {
                    'p1t': p1t,
                    'p1pos': pPos,
                    'p1neg': pNeg,
                    'p1_pos': p1_pos,
                    'p1_neg': p1_neg
                },
                'p0': {
                    'p0t': p0t,
                    'p0pos': pPos,
                    'p0neg': pNeg,
                    'p0_pos': p0_pos,
                    'p0_neg': p0_neg
                }
            }

        return data

    def composeOutput(self):
        result  = self.composeMI()
        fix     = {
            'term': [],
            'total': [],
            'posisi_keseluruhan': [],
            'jumlah_negatif': [],
            'posisi_negatif' : [],
            'jumlah_positif'	: [],
            'posisi_positif' 	: [],
            'mutual_information': []
        }  # dictionaries

        for data in result:
            word 	= fix['term']
            word.append(data)
            fix['term']	= word

            positif = fix['jumlah_positif']
            positif.append(result[data]['positif']['total'])
            fix['jumlah_positif'] = positif

            negatif = fix['jumlah_negatif']
            negatif.append(result[data]['negatif']['total'])
            fix['jumlah_negatif'] = negatif

            total 	= fix['total']
            total.append(result[data]['total'])
            fix['total']	= total

            posAll 	= fix['posisi_keseluruhan']
            posAll.append(result[data]['posisi'])
            fix['posisi_keseluruhan']	= posAll

            posNeg = fix['posisi_negatif']
            posNeg.append(result[data]['negatif']['posisi'])
            fix['posisi_negatif'] = posNeg

            posPos = fix['posisi_positif']
            posPos.append(result[data]['positif']['posisi'])
            fix['posisi_positif'] = posPos

            mi = fix['mutual_information']
            mi.append(result[data]['mi']['value'])
            fix['mutual_information'] = mi

        return fix

    def generateOutput(self):
        output  = self.composeOutput()
        a       = pd.DataFrame(output)

        writer = pd.ExcelWriter(self.fileOutput+'.xlsx', engine='xlsxwriter')
        a.to_excel(writer, sheet_name='Sheet1')
        writer.save()