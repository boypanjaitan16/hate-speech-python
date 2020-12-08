from db import DB

mydb    = DB()

mydb.refactorTable() #create table and populate data
mydb.reorderTableData() #re-order mutual_information of 75% of datas

#only run above code once for the first time to populate datas into database, if it already populated no need to run it again
