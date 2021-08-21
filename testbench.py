import mysql.connector
import csv 
from pygetwindow._pygetwindow_win import cursor
from numpy import require

class CrafterLexica:
    # iterators use this dictionary to find and label relavant data.
    dataminedictionary = {
        'item':'Item.csv',
        'recipe':'Recipe.csv',
        'recipelevel':'RecipeLevelTable.csv',
        'crafttype':'CraftType.csv' #crafttype key is hardcoded to parse CraftType.csv with \\r\\n line terminator, located in loadtable func, CHANGE SOLUTION IF CHANGE KEY
        }
    # tuple structure copied onto new items
    recipeStructure = (
        ('itemid',None),
        ('itemname',None)
        # other item parameters might add later (add as needed to resolve minigame)
        # Crafttype    Recipie Level Table    Item{result}    Item{ammount}    Item{ingredient}[0,9]    Ammount{ingredient}[0,9]    Material Qaulity Factor    Difficulty Factor    Qauilty Factor    Durability Factor    QuickSynthControl    QuickSynthCraftmanship    Secret Recipe Book    CanQuickSynth    CanHq    ExpRewarded    Status{Required}
        )
    datamineLocation = 'ffxiv-datamining-master/csv/'
     
    def getRecipeStruct(self,itemname=None,itemid=None, itemstruct=None, recursion = False):
        if not itemname and not itemid and not itemstruct:
            return None


        if itemstruct==None:
            if itemname and not itemid:
                itemid = self.getItemId(itemname)

            if itemid and not itemname:
                itemname = self.getItemName(itemid)
            itemstruct = dict(self.recipeStructure)
            itemstruct['itemid'] = itemid
            itemstruct['itemname'] = itemname
        else:
            itemid = itemstruct['itemid']
            itemname = itemstruct['itemname']
        #self.tryquery("SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='craftlexica' and `TABLE_NAME`='recipe' AND   `COLUMN_NAME` LIKE '%Amount{I%' or `COLUMN_NAME` LIKE '%Item{I%';")
        #results = self.cursor.fetchall()
        ingredients_start_index = 2;
        sqlquery = "SELECT `CraftType`,`Amount{Result}`,`Item{Ingredient}[0]`,`Amount{Ingredient}[0]`,`Item{Ingredient}[1]`,`Amount{Ingredient}[1]`,`Item{Ingredient}[2]`,`Amount{Ingredient}[2]`,`Item{Ingredient}[3]`,`Amount{Ingredient}[3]`,`Item{Ingredient}[4]`,`Amount{Ingredient}[4]`,`Item{Ingredient}[5]`,`Amount{Ingredient}[5]`,`Item{Ingredient}[6]`,`Amount{Ingredient}[6]`,`Item{Ingredient}[7]`,`Amount{Ingredient}[7]`,`Item{Ingredient}[8]`,`Amount{Ingredient}[8]`,`Item{Ingredient}[9]`,`Amount{Ingredient}[9]` FROM recipe WHERE `Item{Result}`="+str(itemid)+";"
        self.tryquery(sqlquery)
        result = self.cursor.fetchall()
        # return None when no recipe is found
        if len(result) == 0:
            # returns itemstruct with with cancraft termination
            if recursion == True:
                itemstruct['cancraft'] = False
                return itemstruct
            return None
        else:
                itemstruct['cancraft'] = True
            
        # fundamentaly change recipe structure if multiple jobs can craft
        if len(result) > 1 :
            itemstruct['multipleJobsCanCraft']=True
        else:
            itemstruct['multipleJobsCanCraft']=False
            #must use same storage schema for both parts of if/else statement
        for craftoption in result:
            #item struct array
            itemstruct['ingredients_'+self.getCrafttypeName(craftoption[0])]=[]
            itemstruct['resultcount_'+self.getCrafttypeName(craftoption[0])] = craftoption[1]
            index = ingredients_start_index # skip non-ingredients
            while index < len(craftoption):
                #skip empty ingredients
                if craftoption[index]==0 or craftoption[index]<0:
                    index+=2
                    continue

                newitem = dict(self.recipeStructure)
                newitem['itemid'] = craftoption[index]
                newitem['itemname'] = self.getItemName(newitem['itemid'])
                newitem['requiredcount'] = craftoption[(index+1)]

                if recursion == True:
                    newitem = self.getRecipeStruct(itemstruct=newitem, recursion=recursion)
                itemstruct['ingredients_'+self.getCrafttypeName(craftoption[0])].append(newitem)
                index+=2
        return itemstruct
        
    def getBOM(self,recipes, BOM=None, multiplier=1, recursion = False, randomjobassign = True, Tier = 1):
        if BOM == None:
            BOM = {}
        #converts puts recipes into a list if its a dictionary
        if type(recipes) is dict:
            recipes = [recipes]

        for recipe in recipes:
            #item stats
            itemname = recipe['itemname']
            #assumes top level recipe
            requiredcount = 1
            if 'requiredcount' in recipe.keys():
                requiredcount = recipe['requiredcount']
            totalrequiredcount = requiredcount*multiplier
            cancraft = recipe['cancraft']
            jobname = ""

            #item stat storage
            if itemname in BOM.keys():
                #updates item BOM stats
                #multiplier for recursion item multiplying.
                BOM[itemname]['requiredcount'] += totalrequiredcount
                #assign craft tier (higher gets crafted first)
                if BOM[itemname]['Tier'] < Tier:
                    BOM[itemname]['Tier'] = Tier
                jobname = BOM[itemname]['jobname']
            else:
                #enter new item index
                if cancraft:
                    for key in recipe.keys():
                        #jobname starts @ string[12]
                        if 'ingredients_' in key:
                            jobname = key[12:]
                BOM[itemname] = {'requiredcount':totalrequiredcount,
                                 'Tier':Tier,
                                 'jobname':jobname,
                                 'cancraft':cancraft}
            
            #recursion
            if recursion and cancraft:
                newmultiplier = multiplier*requiredcount # passes down qty needed to craft
                Tier+=1 # passes down craft order (inverted, higher goes first)
                for ingredient in recipe['ingredients_'+jobname]:
                    BOM = self.getBOM(ingredient,BOM,multiplier=newmultiplier,recursion=recursion,Tier=Tier)
                    

        return BOM                
            
            
            
            
    def __init__(self, database, cursor, dataBaseName):
        self.cursor = cursor #sql query object
        self.dataBaseName = dataBaseName #what db should I use
        self.tryquery('show databases;')
        self.db = database
        #attempt to create database
        dbname = (dataBaseName,)
        if dbname not in self.cursor.fetchall():
            self.tryquery("CREATE DATABASE {}".format(dbname[0]))

    # get results with self.cursor.fetchall() (fornowanyway), note, returns array, where array index represents result row in form of a tupple; result=[(row1.1,row1.2,..),(row2.1,row2.1,..),..]
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
            
    # expects unquoted string, exact match
    def getKeyvalueId(self,keyvaluename,tablename):
        def quote(inputstring):
            return '"'+inputstring+'"'
        self.tryquery('USE craftlexica;')
        query = 'SELECT '+tablename+'id FROM '+tablename+' WHERE `Name`={}'.format(quote(keyvaluename))
        self.tryquery(query)
        return self.cursor.fetchall()[0][0]
            
    # (integer)itemid: id of target item
    # (string)return: Name of target item
    def getKeyvalueName(self,keyvalueid,tablename):
        self.tryquery('USE craftlexica;')
        query = "SELECT Name FROM "+tablename+" WHERE `"+tablename+"id`={}".format(keyvalueid)
        self.tryquery(query)
        try: 
            return self.cursor.fetchall()[0][0]
        except IndexError as error:
            print(error)
            return None
            
    
    #specialized get functions
    def getItemId(self,itemname):
        return self.getKeyvalueId(itemname, 'item')
            
    def getItemName(self,itemid):
        return self.getKeyvalueName(itemid,'item')

    def getCrafttypeId(self,crafttypename):
        return self.getKeyvalueId(crafttypename, 'crafttype')
            
    def getCrafttypeName(self,crafttypeid):
        return self.getKeyvalueName(crafttypeid,'crafttype')

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

        #use \\r\\n line terminator, which is exclusvie fo CraftType.csv
        lineterminator = '\\n'
        if tablename == 'crafttype':
            lineterminator = '\\r\\n'
            
        #prep table load query
        sqlLoadData = ("LOAD DATA LOCAL INFILE {} INTO TABLE {} FIELDS TERMINATED BY ',' ENCLOSED BY '"+'"'+"' LINES TERMINATED BY '"+lineterminator+"' IGNORE 3 LINES (").format(quote(filelocation), tablename)
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
        
        

