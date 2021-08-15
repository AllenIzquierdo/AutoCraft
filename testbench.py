import mysql.connector
import csv 
#Connector database
db = mysql.connector.connect(host='localhost',user='allen',password='')
cursor = db.cursor()

#create table query
tablename = 'items'
filename = 'Item.csv'
filelocaiton = "'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Item.csv'"
# server accessible filelocaiton = "'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Item.csv'"
cvsfile = csv.reader(open('Item.csv',newline=''))

def backtickquote(inputstring):
    return "`"+inputstring+"`"

def quote(inputstring):
    return '"'+inputstring+'"'

#create master crafter database
cursor.execute('show databases')
dbname = ('mastercrafter',)
if dbname not in cursor.fetchall():
    try:
        cursor.execute("CREATE DATABASE {}".format(dbname[0]))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)
        

#Types dictioanry
#csv type : sql type
typesDict = {
    "int32":"INT NOT NULL",
    "uint32":"INT UNSIGNED NOT NULL",
    "int16":"SMALLINT NOT NULL",
    "uint16":"SMALLINT UNSIGNED NOT NULL",
    "int64":"TINYINT UNSIGNED NOT NULL",
    "str":"TEXT NOT NULL",
    "sbyte":"TINYINT UNSIGNED NOT NULL",
    "byte":"TINYINT NOT NULL"
    }

#skip column index
cvsfile.__next__()

#obtain column descriptors
columnIdentifiers = cvsfile.__next__()
csvColumnTypes = cvsfile.__next__()

#find empty columns, int64 columns are also considered empty becasuse I don't want to dealth with them.
emptyColumnsIndexes = []
for index, value in enumerate(columnIdentifiers):
    if value == '':
        emptyColumnsIndexes.append(index)
        continue
    columnIdentifiers[index] = backtickquote(value)
for index, value in enumerate(csvColumnTypes):
    if value == 'int64':
        emptyColumnsIndexes.append(index)
        continue

#translate column types
sqlColumnTypes = [] #types to put into table
typeExceptions = [] #types not defined in typesDictionary
for index, dataType in enumerate(csvColumnTypes):
    #ommit empty columns, fill with None to reach pairty with column identifier array
    if index in emptyColumnsIndexes:
        sqlColumnTypes.append(None)
        continue
    
    #some datamine dereferences bit locations
    #may want to add derefence location comment in future
    if 'bit&' in dataType:
        #sqlColumnTypes.append('BIT')
        sqlColumnTypes.append('VARCHAR(5)')
        continue
    
    #translate known cvs type to sql type
    if dataType in typesDict.keys():
        sqlColumnTypes.append(typesDict[dataType])
        continue
    
    #catchall, could also be used to link columns to other datamined files
    sqlColumnTypes.append(typesDict['int32'])
    if dataType not in typeExceptions:
        typeExceptions.append(dataType)
#prep delete table query
sqlDropTable = "DROP TABLE {}".format(tablename)
#prep table creation query 
sqlCreateTable = "CREATE TABLE {} (".format(tablename)
for index, columnName, in enumerate(columnIdentifiers):
    #skip empty columns
    if index in emptyColumnsIndexes:
        continue

    if index != 0:#variable seperator
        sqlCreateTable+=','

    sqlCreateTable += columnName +" "+ sqlColumnTypes[index]
sqlCreateTable += ');'

#prep table load query
sqlLoadData = "LOAD DATA INFILE {} INTO TABLE {} FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 3 LINES (".format(filelocaiton, tablename)
for index, columnName in enumerate(columnIdentifiers):
    if index != 0:#variable seperator
        sqlLoadData+=','

    if index in emptyColumnsIndexes:
        sqlLoadData+='@dummy'
    else:
        sqlLoadData+= columnName
sqlLoadData += ");"
    
    

#the lazy debug zone
if False:
    print(emptyColumnsIndexes)
    print(sqlCreateTable) 
    print(sqlLoadData)
    print(columnIdentifiers)
    print(csvColumnTypes)
    print(sqlColumnTypes)
    print(typeExceptions)