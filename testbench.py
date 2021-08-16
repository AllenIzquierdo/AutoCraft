import mysql.connector
import csv 

class CrafterLexica:
    dataminedictionary = {
        'item':'Item.csv',
        'recipe':'Recipe.csv',
        'recipelevel':'RecipeLevelTable.csv',
        'crafttype':'CraftType.csv'
        }
    datamineLocation = 'ffxiv-datamining-master/csv/'
    def __init__(self, database, cursor, dataBaseName):
        self.cursor = cursor #sql query object
        self.dataBaseName = dataBaseName #what db should I use
        self.tryquery('show databases;')
        self.db = database
        #attempt to create database
        dbname = (dataBaseName,)
        if dbname not in self.cursor.fetchall():
            self.tryquery("CREATE DATABASE {}".format(dbname[0]))
    def tryquery(self, query, multi=False):
        try:
            print(query)
            self.cursor.execute(query, multi=multi)
        except mysql.connector.Error as err:
            print("Failed Query: {}".format(err))
            exit(1)

    def autoLoadTables(self):
        self.loadTablesFromFolder(self.datamineLocation, self.dataminedictionary)
        
    def loadTablesFromFolder(self, folderpath, dataminedict):
        for key, filename in dataminedict.items():
            pathtofile = folderpath + filename
            self.loadTable(pathtofile,key)
            

    #file location: location of datamined csv file
    #tablename: the name of the datamine table on mysql database
    def loadTable(self, filelocation, tablename):
        #swap to crafting lexica  database
        self.tryquery('USE {}'.format(self.dataBaseName))
        # server accessible filelocation = "'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Item.csv'"
        cvsfile = csv.reader(open(filelocation,newline=''))

        def backtickquote(inputstring):
            return "`"+inputstring+"`"

        def quote(inputstring):
            return '"'+inputstring+'"'

        #drop table if it exist
        tupletablename = (tablename.lower(),)
        self.tryquery('SHOW TABLES')
        results = self.cursor.fetchall()
        if tupletablename in results:
            self.tryquery("DROP TABLE {}".format(tablename.lower()))

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

        #find empty columns, int64 columns are also considered empty becasuse I don't want to dealth with them and they're uselesse. :)
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

        #prep table creation query 
        sqlCreateTable = "CREATE TABLE {} (".format(tablename)
        for index, columnName, in enumerate(columnIdentifiers):
            #skip empty columns
            if index in emptyColumnsIndexes:
                continue

            if index != 0:#variable seperator
                sqlCreateTable+=','
            if index==0:
                sqlCreateTable += tablename + "id " + sqlColumnTypes[index]
            else:
                sqlCreateTable += columnName +" "+ sqlColumnTypes[index]
        sqlCreateTable += ');'

        #prep table load query
        sqlLoadData = ("LOAD DATA LOCAL INFILE {} INTO TABLE {} FIELDS TERMINATED BY ',' ENCLOSED BY '"+'"'+"' LINES TERMINATED BY '\\n' IGNORE 3 LINES (").format(quote(filelocation), tablename)
        for index, columnName in enumerate(columnIdentifiers):
            if index != 0:#variable seperator
                sqlLoadData+=','

            if index in emptyColumnsIndexes:
                sqlLoadData+='@dummy'
            elif index == 0:
                sqlLoadData += tablename+'id'

            else:
                sqlLoadData += columnName
        sqlLoadData += ");"
        
        #execute querys 
        self.tryquery(sqlCreateTable)
        self.tryquery(sqlLoadData)
        #required when using sql transactional storage engine (server engine is used to load data file)
        #loading data creates a transaction, dbconnection.commit() completes transaction
        self.db.commit() 
        
        #the lazy debug zone
        if False:
            print(emptyColumnsIndexes)
            print(sqlCreateTable) 
            print(sqlLoadData)
            print(columnIdentifiers)
            print(csvColumnTypes)
            print(sqlColumnTypes)
            print(typeExceptions)
        
        

