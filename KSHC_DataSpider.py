import os, datetime, time
#import GISDataSets_10_v4
#from GISDataSets_10_v4 import *  #local modules
import arcpy

#  Class Definitions
###
#######################################################################   
class GISDataSet:
    def __init__(self,fullpath,arcpy):
        objDataSet = arcpy.Describe(fullPath)
        self.name = objDataSet.nameq
        self.catalogPath = objDataSet.catalogPath
        self.catalogPath = objDataSet.dataType

class RasterDataSet(GISDataSet):
    def __init__(self,fullpath,arcpy):
        GISDataSet.__init__(self,fullpath,arcpy)

        thisRas = RasterDataSet(fullpath)

#######################################################################   
###
#  Functions - General Purpose
###
def Int2Digit(integer):
    if integer < 9:
        strInteger = "0"+str(integer)
    else:
        strInteger = str(integer)
    return strInteger

def TimeStampMaker():
    import datetime
    t = datetime.datetime.now()
    strTmonth = Int2Digit(t.month)
    strTday = Int2Digit(t.day)
    strThour = Int2Digit(t.hour)
    strTminute = Int2Digit(t.minute)
    timeStamp = str(t.year)+strTmonth+strTday+strThour+strTminute
    return timeStamp

#######################################################################   
###
#  Functions - GIS Data Set Procedures
###
def lFields(inFC):
    desc = arcpy.Describe(inFC)
    for items in desc.fields:
        print items.name
#######################################################################
def tbxPrintORI(inStr):
    '''a general purpose function for try/except printing
    inside a toolbox function'''
    try:
        arcpy.AddMessage(inStr)
    except:
        print inStr
#######################################################################
def tbxPrint(fBad,inStr):
    '''a general purpose function for try/except printing
    inside a toolbox function'''
    try:
        arcpy.AddMessage(inStr)
        #fBad.write(inStr)
    except:
        print inStr
    finally:
        fBad.write(inStr+"\n")
#######################################################################         
#  Inventory Functions
####################################################################### 
def InventoryWSs(fullPathWS,listWSs,PathAndNameGDB,arcpy):
    ''' A function to list the workspaces
        f(fullPathWS, objListWSs,PathAndNameGDB, objArcPy) 
        returns the listWS list entry [WorkspacePath,WorkspaceType] '''
    arcpy.env.workspace = fullPathWS
    listTemp = []

    # Personal GDB
    listTemp = arcpy.ListWorkspaces("*","Access")
    if len(listTemp) > 0:
        for items in listTemp:
            listWSs.append([items,"PersonalGDB"])
    del listTemp

    # Coverage      
    listTemp = arcpy.ListWorkspaces("*","Coverage")
    if len(listTemp) > 0:
        for items in listTemp:
            #listWSs.append([fullPathWS+"//"+items,"Coverage"])
            listWSs.append([items,"Coverage"])
    del listTemp    

    # FileGDB
    listTemp = arcpy.ListWorkspaces("*","FileGDB")
    if len(listTemp) > 0:
        for items in listTemp:
            listWSs.append([items,"FileGDB"])
    del listTemp  

    # Folders: Shapefiles and Layers
    if len( arcpy.ListFiles('*.shp') ) > 0:
        listWSs.append( [fullPathWS,"Folder_Shp"] )
    if len( arcpy.ListFiles('*.lyr') ) > 0: 
        listWSs.append( [fullPathWS, "Folder_Lyr"] )
    if len( arcpy.ListRasters("*") ) > 0 :
        listWSs.append( [fullPathWS, "Folder_Raster"] )

    # SDE dB
    listTemp = arcpy.ListWorkspaces("*","SDE")
    if len(listTemp) > 0:
        for items in listTemp:
            listWSs.append([items,"SDE"])
    del listTemp 

#######################################################################    
def InventoryFCs(spot,listFCs,arcpy):
    arcpy.env.workspace = spot
    localListFCs = arcpy.ListFeatureClasses()
    for items in localListFCs:
        listFCs.append(spot+"\\"+items)

#######################################################################    
def InventoryTables(spot,listTbl,arcpy):
    arcpy.env.workspace = spot
    localListTbl = arcpy.ListTables()
    for items in localListTbl:
        listTbl.append(spot+"\\"+items)
#######################################################################   
def InventoryRasters(spot,listRas,arcpy):
    arcpy.env.workspace = spot
    localListRas = arcpy.ListRasters()
    for items in localListRas:
        listRas.append(spot+"\\"+items)        
#######################################################################
#  Write Functions
#######################################################################   
def Write_tblWorkspaceTypes(listWSs,PathAndNameGDB,arcpy,listErrors,fBad):    
    # Now - write to the tblWorkspaces
    in_dataset = PathAndNameGDB+"\\"+"tblWorkspaceTypes"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listWSs:
        row = rows.newRow()
        try:
            row.workspace = items[0]
            row.WSType = items[1]
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblWorkspaces')
            listErrors.append([items,"WorkspaceType_Error"])
        finally:
            rows.insertRow(row)
    del rows
#######################################################################   
def Write_tblWorkspaces(listWSs,PathAndNameGDB,arcpy,listErrors,fBad):    
    # Now - write to the tblWorkspaces
    in_dataset = PathAndNameGDB+"\\"+"tblWorkspaces"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listWSs:
        row = rows.newRow()
        try:
            row.workspace = items
        except:
            tbxPrint(fBad,"Workspace "+items+" does not exist or is not supported")
            listErrors.append([items,"Workspace_Error"])
        finally:
            rows.insertRow(row)
    del rows

#######################################################################   
def Write_tblRasters(listRas,PathAndNameGDB,arcpy,listErrors,fBad):
    import os.path
    #pass
    # Now - write to the tblRasters

    in_dataset = PathAndNameGDB+"\\"+"tblRasters"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listRas:
        row = rows.newRow()
        try:
            row.FullPath = items
            row.RasterName = os.path.basename(items)
            row.workspace = os.path.dirname(items)            
            thisRaster = arcpy.Raster(items)
            row.FullPath = thisRaster.catalogPath
            row.UncompressedSize = thisRaster.uncompressedSize
            row.SpatialReference = thisRaster.spatialReference.name
            row.Raster_Format = thisRaster.format
            row.BandCount = thisRaster.bandCount
            row.PixelType = thisRaster.pixelType
            row.NumRows = thisRaster.height
            row.NumColumns = thisRaster.width
            row.CellWidth = thisRaster.meanCellWidth
            row.CellHeight = thisRaster.meanCellHeight
            row.CellValue_Min = thisRaster.minimum
            row.CellValue_Max = thisRaster.maximum
            row.CellValue_Max = thisRaster.maximum
            row.CellValue_Mean = thisRaster.mean
            row.CellValue_StDev = thisRaster.standardDeviation
        except:
            tbxPrint(fBad,"Raster "+items+" does not exist or is not supported")
            listErrors.append([items,"RasterObject_Error"])
        finally:
            rows.insertRow(row)
    try:
        del thisRaster
    finally:
        del rows

#######################################################################   
def Write_tblVectors(listVect,PathAndNameGDB,arcpy,listErrors,fBad):
    import os.path
    #pass
    # Now - write to the tblVectors

    in_dataset = PathAndNameGDB+"\\"+"tblVectors"
    rows = arcpy.InsertCursor(in_dataset)

    for items in listVect:
        row = rows.newRow()
        try:
            row.FullPath = items
            thisVector = arcpy.Describe(items)           
            row.FCName = thisVector.file
            row.workspace = os.path.dirname(items)
            row.SpatialReference = thisVector.spatialReference.name
            row.Vector_DataType = thisVector.dataType
            row.NumFeatures = int(arcpy.GetCount_management(items)[0])
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblVectors')
            listErrors.append([items,"VectorObject_Error"])
        finally:
            rows.insertRow(row)
    del rows
####################################################################### 
def Write_tblErrors(listErrors,PathAndNameGDB,arcpy,fBad):
    import os.path
    #pass
    # Now - write to the tblRasters

    in_dataset = PathAndNameGDB+"\\"+"tblErrors"
    rows = arcpy.InsertCursor(in_dataset)

    for items in listErrors:
        #try:
        #thisVector = arcpy.Describe(items)
        row = rows.newRow()
        try:
            row.DataSet = items[0]
            row.Workspace = os.path.dirname(items[0])
            row.DataSet_name = os.path.basename(items[0])
            row.ErrorType = items[1]
        except:
            tbxPrint(fBad,'problem with writing '+items[0]+' to tblErrors')
        finally:
            rows.insertRow(row)
    del rows
#######################################################################
def Write_tblExtentErrors(listExtErrors,PathAndNameGDB,arcpy,fBad):
    import os.path
    #pass
    # Now - write to the tblRasters

    in_dataset = PathAndNameGDB+"\\"+"tblExtentErrors"
    rows = arcpy.InsertCursor(in_dataset)

    for items in listExtErrors:
        #try:
        #thisVector = arcpy.Describe(items)
        row = rows.newRow()
        try:
            row.DataSet = items
            row.Workspace = os.path.dirname(items)
            row.DataSet_name = os.path.basename(items)
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblExtentErrors')
        finally:
            rows.insertRow(row)
    del rows
#######################################################################
def Write_tblTables(listTbl,PathAndNameGDB,arcpy,listErrors,fBad):
    import os.path
    #pass
    # Now - write to the tblTables

    in_dataset = PathAndNameGDB+"\\"+"tblTables"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listTbl:
        row = rows.newRow()
        try:
            row.FullPath = items
            row.TableName = os.path.basename(items)
            row.workspace = os.path.dirname(items)
            thisTable = arcpy.Describe(items)
            row.NumRows   = int(arcpy.GetCount_management(items)[0])
            row.TableType = thisTable.datasetType            
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblTables')
            listErrors.append([items,"Table_Error"])
        finally:
            rows.insertRow(row)
    del rows    
####################################################################### 
#  Write Extent
#######################################################################
def Write_vectExtentFC(listFCs,PathAndNameExtentFC,arcpy,listErrors,flagUnknownExtent,fBad):
    for FCs in listFCs:
        try:
            
            Write_simpleExtent_v2(FCs,PathAndNameExtentFC,arcpy,listErrors,flagUnknownExtent,fBad)
        except:
            tbxPrint(fBad, "  Problem with "+FCs+"; no Extent Generated")
            listErrors.append(FCs)            
####################################################################### 
def Write_rasExtentFC(listRas,PathAndNameExtentFC,arcpy,listErrors,flagUnknownExtent,fBad):
    for Ras in listRas:
        try:
            Write_simpleRasExtent_v3(Ras,PathAndNameExtentFC,arcpy,listErrors,flagUnknownExtent,fBad)
        except:
            tbxPrint(fBad, "  Problem with "+Ras+"; no Extent Generated")
            listErrors.append(Ras)
#######################################################################

####################################################################### 
def Write_simpleRasExtent_v3(inRas,extentPoly,arcpy,listErrors,flagUnknownExtent,fBad):    
    # Feature extent
    #
    #arcpy.Delete_management("in_memory")
    import os.path
    tbxPrint(fBad,"Creating Extent for "+inRas)
    objRas = arcpy.Raster(inRas)

    extent = objRas.extent
    objSpatialRef = objRas.spatialReference
    SpatialRef = objRas.spatialReference.name

    thisRaster = objRas
    workspace = os.path.dirname(objRas.catalogPath)
    UncompressedSize = thisRaster.uncompressedSize
    SpatialReference = thisRaster.spatialReference.name
    Raster_Format = thisRaster.format
    BandCount = thisRaster.bandCount
    PixelType = thisRaster.pixelType
    NumRows = thisRaster.height
    NumColumns = thisRaster.width
    CellWidth = thisRaster.meanCellWidth
    CellHeight = thisRaster.meanCellHeight
    CellValue_Min = thisRaster.minimum
    CellValue_Max = thisRaster.maximum
    CellValue_Max = thisRaster.maximum
    CellValue_StDev = thisRaster.standardDeviation
    
    # Array to hold points
    array = arcpy.Array()
    # Create the bounding box
    array.add(extent.lowerLeft)
    array.add(extent.lowerRight)
    array.add(extent.upperRight)
    array.add(extent.upperLeft)
    # ensure the polygon is closed
    array.add(extent.lowerLeft)
    # Create the polygon object
    polygon = arcpy.Polygon(array)
    array.removeAll()

    # Insert Cursor, insert new shape
    featDesc = arcpy.Describe( extentPoly )
    srWGS84 = arcpy.Describe(extentPoly).SpatialReference

    flagAssumedSpatialRef = False
    flagAssumedProjOrGCS = ""

    if SpatialRef == "Unknown":
        if not flagUnknownExtent:
            #print "UNKNOWN FLAG"
            return # Give up on the geometry

        if extent.XMax > 180:
            tbxPrint(fBad,desc.file+" has an unknown spatial reference, but seems to be in projected units ")
            flagAssumedProjOrGCS = "Projected"
            flagAssumedSpatialRef = True
            SpatialRef = SpatialRef+"__assumed_Projected"
        else:
            tbxPrint(fBad,desc.file+" has an unknown spatial reference, but seems to be in GCS ")
            flagAssumedProjOrGCS = "GCS"
            flagAssumedSpatialRef = True
            SpatialRef = SpatialRef+"__assumed_GCS"

    cur = arcpy.InsertCursor(extentPoly, thisRaster.spatialReference )
    
    feat = cur.newRow()
    # Populate the fields
    inDesc = arcpy.Describe(extentPoly)    
    feat.setValue(inDesc.shapeFieldName,polygon)
    feat.data_model = "raster"	
    feat.spatial_ref = SpatialReference
    feat.data_type = "Raster__"+Raster_Format+"_"+str(BandCount)+"x"+PixelType
    feat.path = thisRaster.catalogPath
    feat.name = thisRaster.name
    feat.workspace = os.path.dirname(inRas)
    cur.insertRow(feat)

    del feat,cur
    del polygon
#######################################################################   
def Write_simpleExtent_v2(inFC,extentPoly,arcpy,listErrors,flagUnknownExtent,fBad):
    import os.path
    tbxPrint(fBad,"Creating Extent for "+inFC)
    #try: 
    desc = arcpy.Describe(inFC)
    extent = desc.extent
    objSpatialRef = desc.SpatialReference
    SpatialRef = desc.SpatialReference.name
    data_type = desc.shapeType+"__"+desc.featureType
    
    # Array to hold points
    array = arcpy.Array()
    # Create the bounding box
    array.add(extent.lowerLeft)
    array.add(extent.lowerRight)
    array.add(extent.upperRight)
    array.add(extent.upperLeft)
    # ensure the polygon is closed
    array.add(extent.lowerLeft)
    # Create the polygon object
    polygon = arcpy.Polygon(array)
    array.removeAll()
    
    # Insert Cursor, insert new shape
    featDesc = arcpy.Describe( extentPoly )
    srWGS84 = arcpy.Describe(extentPoly).SpatialReference

    flagAssumedSpatialRef = False
    flagAssumedProjOrGCS = ""

    if SpatialRef == "Unknown":
        if not flagUnknownExtent:
            #print "UNKNOWN FLAG"
            return # Give up on the geometry

        if extent.XMax > 180:
            tbxPrint(fBad, desc.file+" has an unknown spatial reference, but seems to be in projected units ")
            flagAssumedProjOrGCS = "Projected"
            flagAssumedSpatialRef = True
            SpatialRef = SpatialRef+"__assumed_Projected"
        else:
            tbxPrint(desc.file+" has an unknown spatial reference, but seems to be in GCS ")
            flagAssumedProjOrGCS = "GCS"
            flagAssumedSpatialRef = True
            SpatialRef = SpatialRef+"__assumed_GCS"

    cur = arcpy.InsertCursor(extentPoly, desc.SpatialReference )
    feat = cur.newRow()

    #print "here"
    inDesc = arcpy.Describe(extentPoly)    
    feat.setValue(inDesc.shapeFieldName,polygon)

    
    feat.path = inFC
    feat.workspace = os.path.dirname(inFC)
    feat.spatial_ref = SpatialRef
    feat.data_type = data_type
    feat.data_model = "vector"
    feat.name = desc.file


    cur.insertRow(feat)

    del feat,cur
    del polygon
#######################################################################   



###
#  Time Stamp
###
timeStamp = ""
timeStamp = TimeStampMaker()

###
#  subroutines
###
def Create_ExtentFC(inputGDB,FCName,strSuffix=timeStamp):
    wsGDB = inputGDB

    strSR = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433],AUTHORITY["EPSG",4326]]'
    objWGS84 = arcpy.CreateSpatialReference_management(strSR)
    arcpy.CreateFeatureclass_management(wsGDB,FCName,"POLYGON","#","DISABLED","DISABLED",objWGS84)

    arcpy.AddField_management(wsGDB+"\\"+FCName, "name", "text","50")    
    arcpy.AddField_management(wsGDB+"\\"+FCName, "path", "text", "256")
    arcpy.AddField_management(wsGDB+"\\"+FCName, "workspace", "text", "256")
    arcpy.AddField_management(wsGDB+"\\"+FCName, "spatial_ref", "text", "50")
    arcpy.AddField_management(wsGDB+"\\"+FCName, "data_model","text","50")
    arcpy.AddField_management(wsGDB+"\\"+FCName, "data_type", "text", "50")
    arcpy.AddField_management(wsGDB+"\\"+FCName, "extent_quality","text","10")
    #arcpy.AddField_management(wsGDB+"\\"+FCName,"NumFeatures","LONG")
    #arcpy.AddGlobalIDs_management(wsGDB+"\\"+FCName)
    arcpy.AddField_management(wsGDB+"\\"+FCName, "GUID_VectRas","GUID")
    arcpy.AddField_management(wsGDB+"\\"+FCName, "GUID_Workspaces","GUID")
    return

def Create_DataSpiderGDB(GDBFileLoc,timestamp,GDBName = None, FCName = None):
    '''Creates a DataSpider GDB: 
               inputs :  GDBFileLocation <path>, timestamp <string>, {GDB Name} <string; override default>
               returns:  pathNameGDB <path and name of resulting GDB> 
    '''
    if GDBName: 
        fGDBName = GDBName+"_"+timestamp
    else:
        fGDBName = "DataSpiderInventory_"+timestamp
    if FCName:
        ExtentFCName = FCName
    else: 
        ExtentFCName = "ExtentsWGS84"#_"+timeStamp

        
    arcpy.CreateFileGDB_management(GDBFileLoc,fGDBName,"CURRENT")
    pathNameGDB = GDBFileLoc+fGDBName+".gdb"
    ###
    # Create Contents of GDB
    ###
    Create_tblWorkspaces(pathNameGDB)
    Create_tblWorkspaceTypes(pathNameGDB)
    Create_tblRasters(pathNameGDB)
    Create_tblVectors(pathNameGDB)
    Create_ExtentFC(pathNameGDB, ExtentFCName)
    Create_tblErrors(pathNameGDB)
    Create_tblExtErrors(pathNameGDB)
    Create_tblTables(pathNameGDB)
    return pathNameGDB,ExtentFCName
    
def Create_tblWorkspaces(inputGDB,tblName = "tblWorkspaces"):
    arcpy.CreateTable_management(inputGDB,tblName)
    pathName = inputGDB+"\\"+tblName
    result = arcpy.AddField_management(pathName,"workspace","TEXT","256")
    result = arcpy.AddGlobalIDs_management(pathName)

def Create_tblWorkspaceTypes(inputGDB,tblName = "tblWorkspaceTypes"):
    arcpy.CreateTable_management(inputGDB,tblName)
    pathName = inputGDB+"\\"+tblName
    result = arcpy.AddField_management(pathName,"workspace","TEXT","256")
    result = arcpy.AddField_management(pathName,"WSType","TEXT","25")
    result = arcpy.AddGlobalIDs_management(pathName)
    
def Create_tblErrors(inputGDB,tblName = "tblErrors"):
    arcpy.CreateTable_management(inputGDB,tblName)
    pathName = inputGDB+"\\"+tblName
    result = arcpy.AddField_management(pathName,"DataSet","TEXT","256")
    result = arcpy.AddField_management(pathName,"Workspace","TEXT","256")
    result = arcpy.AddField_management(pathName,"DataSet_name","TEXT","100")
    result = arcpy.AddField_management(pathName,"ErrorType","TEXT","100")
    result = arcpy.AddGlobalIDs_management(pathName)
def Create_tblExtErrors(inputGDB,tblName = "tblExtentErrors"):
    arcpy.CreateTable_management(inputGDB,tblName)
    pathName = inputGDB+"\\"+tblName
    result = arcpy.AddField_management(pathName,"DataSet","TEXT","256")
    result = arcpy.AddField_management(pathName,"Workspace","TEXT","256")
    result = arcpy.AddField_management(pathName,"DataSet_name","TEXT","100")
    result = arcpy.AddGlobalIDs_management(pathName)    
def Create_tblRasters(inputGDB,tblName = "tblRasters"):
    arcpy.CreateTable_management(inputGDB,tblName)
    pathName = inputGDB+"\\"+tblName
    result = arcpy.AddField_management(pathName,"FullPath","TEXT","256")
    result = arcpy.AddField_management(pathName,"RasterName","TEXT","256")
    result = arcpy.AddField_management(pathName,"workspace","TEXT","256")
    result = arcpy.AddField_management(pathName,"UncompressedSize","DOUBLE")
    result = arcpy.AddField_management(pathName,"SpatialReference","TEXT","30")
    result = arcpy.AddField_management(pathName,"Raster_Format","TEXT","25")
    result = arcpy.AddField_management(pathName,"BandCount","SHORT")
    result = arcpy.AddField_management(pathName,"PixelType","TEXT","5")
    result = arcpy.AddField_management(pathName,"NumRows","LONG")
    result = arcpy.AddField_management(pathName,"NumColumns","LONG")
    result = arcpy.AddField_management(pathName,"CellWidth","DOUBLE")
    result = arcpy.AddField_management(pathName,"CellHeight","DOUBLE")
    #stats
    result = arcpy.AddField_management(pathName,"CellValue_Min","DOUBLE")
    result = arcpy.AddField_management(pathName,"CellValue_Max","DOUBLE")
    result = arcpy.AddField_management(pathName,"CellValue_Mean","DOUBLE")
    result = arcpy.AddField_management(pathName,"CellValue_StDev","DOUBLE")
    result = arcpy.AddGlobalIDs_management(pathName)

def Create_tblTables(inputGDB,tblName = "tblTables"):
    arcpy.CreateTable_management(inputGDB,tblName)
    pathName = inputGDB+"\\"+tblName
    result = arcpy.AddField_management(pathName,"FullPath","TEXT","256")
    result = arcpy.AddField_management(pathName,"TableName","TEXT","256")
    result = arcpy.AddField_management(pathName,"workspace","TEXT","256")
    result = arcpy.AddField_management(pathName,"NumRows","LONG")
    result = arcpy.AddField_management(pathName,"TableType","TEXT","5")
    result = arcpy.AddGlobalIDs_management(pathName)
    
def Create_tblVectors(inputGDB,tblName = "tblVectors"):
    arcpy.CreateTable_management(inputGDB,tblName)
    pathName = inputGDB+"\\"+tblName
    result = arcpy.AddField_management(pathName,"FullPath","TEXT","256")
    result = arcpy.AddField_management(pathName,"FCName","TEXT","256")
    result = arcpy.AddField_management(pathName,"workspace","TEXT","256")
    #result = arcpy.AddField_management(pathName,"UncompressedSize","DOUBLE")
    result = arcpy.AddField_management(pathName,"SpatialReference","TEXT","30")
    result = arcpy.AddField_management(pathName,"Vector_DataType","TEXT","25")
    result = arcpy.AddField_management(pathName,"NumFeatures","LONG")
    result = arcpy.AddGlobalIDs_management(pathName)
    
###
#  declare parameters 
###
items = []
tbl = "tblDataInventory"

listWSs  = [] #  list for Workspaces
listGDBs = [] #  list for GDBs
listLYRs = [] #  list for layer files
listRas  = [] #  list for raster files
listFCs  = [] #  list for FCs
listTbl  = [] #  list for Tables
listExtErrors = []


#vertex_array = arcpy.CreateObject("Array") # store 4pts for extent

###
#  Initialize the tool parameters:  input or defaults
###

if arcpy.GetParameterAsText(0):
    targetDir = arcpy.GetParameterAsText(0)
else:
    #targetDir = "C:\\Scratch"
    targetDir = "N:\\SHC\\2_Projects\\022_ScottRiparian"

if arcpy.GetParameterAsText(1):
    GDBFileLoc = arcpy.GetParameterAsText(1)
    if GDBFileLoc[-1] != u'\\':
        GDBFileLoc = GDBFileLoc+ "\\"    
else:
    GDBFileLoc = "R:\\"
    
if arcpy.GetParameterAsText(2):
    logBadData = arcpy.GetParameterAsText(2)
else:
    logBadData = "R:\\testScottRip"
    
if arcpy.GetParameterAsText(3):
    FCName = arcpy.GetParameterAsText(3)
else:
    FCName = "ExtentsWGS84"#+timeStamp

if arcpy.GetParameterAsText(4):
    GDBName = arcpy.GetParameterAsText(4)
else:
    GDBName = None

if arcpy.GetParameterAsText(5):
    flagUnknownExtent = arcpy.GetParameterAsText(5)
else:
    flagUnknownExtent = False

###
#  Create Output Files
###
#output log Bad Data    
fBad = open(logBadData+"_"+timeStamp+".txt",'w')
#output GDB
PathAndNameGDB,ExtentFCName = Create_DataSpiderGDB(GDBFileLoc,timeStamp,GDBName)
tbxPrint(fBad,"\n \n \n Created "+PathAndNameGDB)
tbxPrint(fBad,"\n       with log file "+logBadData+"\n \n ")
time.sleep(5)


tbxPrint(fBad," \n  Starting Inventory from "+targetDir+" \n \n" )
listWalk = []
for root,dirs,files in os.walk(targetDir):
    previousRoot,previousDirs,previousFiles = "","",""
    listWalk.append( (root,dirs,files) )
    if len(dirs) > 0:
        arcpy.AddMessage(root)
    else:  
        arcpy.AddMessage("      ----> "+root)

#inventory = []   #inventory holds the list of 

###
#     Main Event :  Iterate on all root locations in the inventory
###

for places in listWalk:    #  This is the inventory loop:  items contains [ [root],[dirs],[files] ]
    #am I a raster folder?
    try:
        testRas = arcpy.Raster(places[0])
        del testRas
    except:        
        arcpy.env.workspace = places[0]  # set our WS to the root element
        tbxPrint(fBad,"Inventory for "+places[0])
        tbxPrint(fBad,"    ---->  Starting Inventory: Workspaces")
        InventoryWSs(places[0],listWSs,PathAndNameGDB,arcpy)
        tbxPrint(fBad,"    ---->  Starting Inventory: Feature Classes")
        InventoryFCs(places[0],listFCs,arcpy)
        tbxPrint(fBad,"    ---->  Starting Inventory: Rasters")
        InventoryRasters(places[0],listRas,arcpy)
        tbxPrint(fBad,"    ---->  Starting Inventory: Tables")
        InventoryTables(places[0],listTbl,arcpy)

listErrors = []
tbxPrint(fBad,"\n \n \n Generating Tables:")
tbxPrint(fBad,"        ---->  tblWorkspaceTypes")
if len(listWSs) > 0:
    Write_tblWorkspaceTypes(listWSs,PathAndNameGDB,arcpy,listErrors,fBad)

    setWS = set()
    for items in listWSs:
        setWS.add(items[0])
    listSetWS = []
    for items in setWS:
        listSetWS.append(items)
    
tbxPrint(fBad,"\n        ---->  tblWorkspaces")
if len(listSetWS) > 0:
    Write_tblWorkspaces(listSetWS,PathAndNameGDB,arcpy,listErrors,fBad)
tbxPrint(fBad, "\n        ---->  tblRasters")
if len(listRas) > 0:
    Write_tblRasters(listRas,PathAndNameGDB,arcpy,listErrors,fBad)
tbxPrint(fBad, "\n        ---->  tblFeatureClasses")
if len(listFCs) > 0:
    Write_tblVectors(listFCs,PathAndNameGDB,arcpy,listErrors,fBad)
tbxPrint(fBad, "\n        ---->  tblTables")
if len(listTbl) > 0:
    Write_tblTables(listTbl,PathAndNameGDB,arcpy,listErrors,fBad)

#Write_tblRasters(listRas,PathAndNameGDB,arcpy)
tbxPrint(fBad, "\n \n \n Generating Extent Feature Class:" )
tbxPrint(fBad, "        ---->  For Vector Data")
extentFC = PathAndNameGDB+"\\"+ExtentFCName
if len(listFCs) > 0:
    Write_vectExtentFC(listFCs,PathAndNameGDB+"\\"+ExtentFCName,arcpy,listExtErrors,flagUnknownExtent,fBad)
tbxPrint (fBad,"\n         ---->  For Raster Data")
if len(listRas) > 0:
    Write_rasExtentFC(listRas,PathAndNameGDB+"\\"+ExtentFCName,arcpy,listExtErrors,flagUnknownExtent,fBad)
tbxPrint(fBad, " ")

Write_tblErrors(listErrors,PathAndNameGDB,arcpy,fBad)
Write_tblExtentErrors(listExtErrors,PathAndNameGDB,arcpy,fBad)



#  Worth refactoring?
arcpy.MakeFeatureLayer_management(extentFC, "lyr")

arcpy.AddJoin_management("lyr","path",PathAndNameGDB+"\\tblRasters","FullPath")
arcpy.SelectLayerByAttribute_management("lyr","NEW_SELECTION", """ "data_model" = 'raster' """)
arcpy.CalculateField_management("lyr",u'GUID_VectRas',"[tblRasters.GlobalID]","VB","#")
arcpy.RemoveJoin_management("lyr","tblRasters")

arcpy.AddJoin_management("lyr","path",PathAndNameGDB+"\\tblVectors","FullPath")
arcpy.SelectLayerByAttribute_management("lyr","NEW_SELECTION", """ "data_model" = 'vector' """)
arcpy.CalculateField_management("lyr",u'GUID_VectRas',"[tblVectors.GlobalID]","VB","#")
arcpy.RemoveJoin_management("lyr","tblVectors")

arcpy.AddJoin_management("lyr","workspace",PathAndNameGDB+"\\tblWorkspaces","workspace")
arcpy.SelectLayerByAttribute_management("lyr","NEW_SELECTION","#")
arcpy.CalculateField_management("lyr",u'GUID_Workspaces',"[tblWorkspaces.GlobalID]","VB","#")

arcpy.Delete_management("lyr")

tbxPrint(fBad, " ")
tbxPrint(fBad, " ")
tbxPrint(fBad, "  Finished Inventory.")
tbxPrint(fBad,"\n  Created "+PathAndNameGDB)
tbxPrint(fBad,"\n       with log file "+logBadData+"\n \n ")

