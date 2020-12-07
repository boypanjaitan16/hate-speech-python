import mysql.connector
import json
import math

from process import Process

class DB:
    tableName   = 'train_result'
    def __init__(self):
        mydb = mysql.connector.connect(
            host    ="localhost",
            user    ="root",
            password="B0yd@nnoah",
            database="hatespeech"
        )

        mycursor = mydb.cursor()

        self.mydb       = mydb
        self.mycursor   = mycursor

    def prepareTable(self):
        # try:
        self.mycursor.execute("SELECT * FROM information_schema.tables WHERE table_name = '"+self.tableName+"'")

        total   = len(self.mycursor.fetchall())

        if total < 1:
            self.mycursor.execute("CREATE TABLE `"+self.tableName+"` (`term` varchar(255) NOT NULL,`total` int DEFAULT 0,`negatif` int DEFAULT 0,`positif` int DEFAULT 0,`mutual_information` double DEFAULT 0, PRIMARY KEY (`term`))")
            self.populateData()
        else:
            self.populateData()
        # except Exception as e:
        #     print(e)

    def populateData(self):
        process = Process()
        # try:
        self.mycursor.execute('TRUNCATE TABLE ' + self.tableName)

        mi  = process.composeMI()

        # print(json.dumps(mi, indent=4))

        for row in mi:
            query   = "INSERT INTO "+self.tableName+" (term, total, negatif, positif, mutual_information) VALUES (%s, %s, %s, %s, %s)"
            values  = (row, mi[row]['total'], mi[row]['negatif']['total'], mi[row]['positif']['total'], mi[row]['mi']['value'])
            self.mycursor.execute(query, values)
            self.mydb.commit()

            print('term "'+row+'" inserted')
        # except Exception as e:
        #     print(e)

    def refactorTable(self):
        self.mycursor.execute("DROP TABLE IF EXISTS `"+self.tableName+"`")
        self.prepareTable()

    def reorderTableData(self):
        self.mycursor.execute("SELECT count(term) FROM "+self.tableName)

        result  = self.mycursor.fetchone()
        total   = result[0]

        per75   = math.ceil((75/100) * total)

        self.mycursor.execute("SELECT * FROM "+self.tableName+" ORDER BY mutual_information DESC LIMIT "+str(per75))

        fresh   = self.mycursor.fetchall()

        self.mycursor.execute('TRUNCATE TABLE '+self.tableName)

        for row in fresh:
            query   = "INSERT INTO " + self.tableName + " (term, total, negatif, positif, mutual_information) VALUES (%s, %s, %s, %s, %s)"
            values  = (row[0], row[1], row[2], row[3], row[4])
            self.mycursor.execute(query, values)
            self.mydb.commit()

        print('table data re-ordered successfully to 75%')

    def validateWords(self, value, name):
        process = Process()
        terms   = process.cleanComment(value)
        pPos    = []
        pNeg    = []

        tPos = 0
        tNeg = 0

        for word in terms:
            self.mycursor.execute("SELECT * FROM " + self.tableName + " WHERE term='" + word + "'")
            # rows.append()
            res = self.mycursor.fetchone()

            if res == None:
                pPos.append(0)
                pNeg.append(0)

                tPos += 0
                tNeg += 0
            else:
                vPos = res[3] / (res[3] + res[2]) if res[3] > 0 else 0
                vNeg = res[2] / (res[3] + res[2]) if res[2] > 0 else 0
                pPos.append(vPos)
                pNeg.append(vNeg)

                tPos += vPos
                tNeg += vNeg

            # print("Tidak ada" if res == None else res)

        tPos = math.exp(tPos)
        tNeg = math.exp(tNeg)

        sum = tPos + tNeg

        tPos = tPos / sum
        tNeg = tNeg / sum

        result = 'Positif' if tPos > tNeg else 'Negatif'

        return {
            'nama'      : name,
            'komentar'  : value,
            'positif'   : tPos,
            'negatif'   : tNeg,
            'hasil'     : result
        }
