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
            self.mycursor.execute("CREATE TABLE `"+self.tableName+"` (`term` varchar(255) NOT NULL,`total_negatif` int DEFAULT 0,`total_positif` int DEFAULT 0,`total_term` int DEFAULT 0, `df_positif` int DEFAULT 0, `df_negatif` int DEFAULT 0, `df_total` int DEFAULT 0, `n11` int DEFAULT 0, `n01` int DEFAULT 0, `n10` int DEFAULT 0, `n00` int DEFAULT 0, `mi` double DEFAULT 0, PRIMARY KEY (`term`))")
            self.populateData()
        else:
            print('none')
            self.populateData()
        # except Exception as e:
        #     print(e)

    def populateData(self):
        process = Process()
        # try:
        self.mycursor.execute('TRUNCATE TABLE ' + self.tableName)
        totalNeg    = 0
        totalPos    = 0

        mi  = process.composeData()

        for row in mi:
            totalNeg += mi[row]['negatif']['total']
            totalPos += mi[row]['positif']['total']
        

        n   = totalNeg+totalPos
        for row in mi:
            query       = "INSERT INTO "+self.tableName+" (term, total_negatif, total_positif, total_term, df_positif, df_negatif, df_total, n11, n01, n10, n00, mi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            n11pos     = mi[row]['positif']['total']
            n01pos     = (totalPos - mi[row]['positif']['total'])
            n10pos     = mi[row]['negatif']['total']
            n00pos     = (totalNeg - mi[row]['negatif']['total'])
            
            n11neg     = mi[row]['negatif']['total']
            n01neg     = (totalNeg - mi[row]['negatif']['total'])
            n10neg     = mi[row]['positif']['total']
            n00neg     = (totalPos - mi[row]['positif']['total'])
            
            n1_pos     = n10pos+n11pos
            n1pos      = n01pos+n11pos
            n0_pos     = n01pos+n00pos
            n0pos      = n10pos+n00pos
            
            n1_neg     = n10neg+n11neg
            n1neg      = n01neg+n11neg
            n0_neg     = n01neg+n00neg
            n0neg      = n10neg+n00neg            
            
            rpos       = (n11pos/n)*(process.cleanLog2((n*n11pos), (n1_pos*n1pos)))
            spos       = (n01pos/n)*(process.cleanLog2((n*n01pos), (n0_pos*n1pos)))
            tpos       = (n10pos/n)*(process.cleanLog2((n*n10pos), (n1_pos*n0pos)))
            upos       = (n00pos/n)*(process.cleanLog2((n*n00pos), (n0_pos*n0pos)))

            rneg       = (n11neg/n)*(process.cleanLog2((n*n11neg), (n1_neg*n1neg)))
            sneg       = (n01neg/n)*(process.cleanLog2((n*n01neg), (n0_neg*n1neg)))
            tneg       = (n10neg/n)*(process.cleanLog2((n*n10neg), (n1_neg*n0neg)))
            uneg       = (n00neg/n)*(process.cleanLog2((n*n00neg), (n0_neg*n0neg)))
            
            MIpos = rpos+spos+tpos+upos
            MIneg = rneg+sneg+tneg+uneg
            finalMI = MIpos if MIpos >= MIneg else MIneg

            dfTotal     = (mi[row]['positif']['df'] + mi[row]['negatif']['df'])
            valuesPos   = (row, mi[row]['negatif']['total'], mi[row]['positif']['total'], mi[row]['total'], mi[row]['positif']['df'], mi[row]['negatif']['df'], dfTotal, n11, n01, n10, n00, finalMI)
            self.mycursor.execute(query, valuesPos)

            self.mydb.commit()

        #     print('term "'+row+'" inserted')

    def refactorTable(self):
        self.mycursor.execute("DROP TABLE IF EXISTS `"+self.tableName+"`")
        self.prepareTable()

    def reorderTableData(self):
        self.mycursor.execute("SELECT count(term) FROM "+self.tableName)

        result  = self.mycursor.fetchone()
        total   = result[0]

        per75   = math.ceil((75/100) * total)

        self.mycursor.execute("SELECT * FROM "+self.tableName+" ORDER BY mi DESC LIMIT "+str(per75))

        fresh   = self.mycursor.fetchall()

        self.mycursor.execute('TRUNCATE TABLE '+self.tableName)

        for row in fresh:
            query       = "INSERT INTO "+self.tableName+" (term, total_negatif, total_positif, total_term, df_positif, df_negatif, df_total, n11, n01, n10, n00, mi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            values  = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11])
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
