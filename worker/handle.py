import numpy as np
import pandas as pandas
import csv as csv
import math as math
import requests
import json
import time
from logger import getLogger
from dotenv import dotenv_values

from requestModel import RequestModel

config = dotenv_values(".env")

SERVICE = "Handle"
WEB_HOOK = config.get("WEB_HOOK_URL")
UPLOAD_PATH = config.get("PATH_UPLOAD_FOLDER")
np.set_printoptions(linewidth=np.inf)
DontShowDebug = False
K_neighbors_values = 2


def execute(fileName):

    # SEED Handle. Sleep 5s send notification to asp.net hook

    pathFile = UPLOAD_PATH+fileName
    getLogger().info(f'[{SERVICE}] In-progressing...')
    getLogger().info(f'[{SERVICE}] Handling path file {pathFile}...')
    
    # time.sleep(5)


    fo = open(pathFile, "r")
    getLogger().info(f'Name of the file: {fo.name}')

    # line = fo.read(100)
    # getLogger().info("Read Line: " + line)

    # Close opened file
    # fo.close()

    # TODO: Call function logic handle
    data = recommendation(fo)
    # SEED handle. Sleep 3s send notification to asp.net hook
    url = WEB_HOOK

    payload = json.dumps({
        'data': {
            'listUserId': data.list_user_id,
            'listProductId': data.list_product_id,
            'normalize': data.normailize
        }
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        #Not handle error yet!!!!!
        getLogger().error(f'[{SERVICE}] ERROR: {response.text}')
        return False
    return True

    ###


# TODO: Do logic

def recommendation(upload):
    # DontShowDebug = False
    # Enviroment variables
    K_neighbors_values = 2

    # Ecom_Data = open(next(iter(upload)))

    # type(upload)

    csvreader = csv.reader(upload)

    # Extract the files header

    header = []
    header = next(csvreader)
    getLogger().info(header)

    # Extract the records

    rows = []

    for row in csvreader:
        rows.append(row)

    Extracted = Export_dataframe_rating(rows)

    Converted, UserIdsArray, ProductIdsArray = Convert_DTFrame(Extracted)

    Normalized = Data_Normilization(Converted)

    getLogger().info(f'Normalized...{Normalized}')

    resultOfSimilarity = Cosine_Similarity(Normalized)

    final = Rating_Guessing_func(K_neighbors_values, resultOfSimilarity, Normalized, ProductIdsArray, UserIdsArray)


    requestModel = RequestModel()
    requestModel.list_product_id = [int(numeric_string) for numeric_string in ProductIdsArray]
    requestModel.list_user_id = [int(numeric_string) for numeric_string in UserIdsArray]
    requestModel.normailize = final.data.tolist()

    getLogger().info(f'final...{final}')
    return requestModel


def get_datafarame_ratings_base(text, header,rows):

    ratings = pandas.read_csv(text, sep=',', names=header)
    getLogger().info(f'ratings...{ratings}')
    # print(ratings)
    getLogger().info(f'ratings.value...{ratings.values}')
    Y_data = ratings.values

    return header.append(rows)


def Converted(UserIdsArray, ProductIdsArray, Extracted):
    convert = [['x' for i in range(len(UserIdsArray))]
               for j in range(len(ProductIdsArray))]

    for element in Extracted[1:]:
        userIndex = UserIdsArray.index(element[0])
        productIndex = ProductIdsArray.index(element[1])
        convert[productIndex][userIndex] = element[2]

    print(convert)

    return convert


def Convert_DTFrame(extracted):

  #Create User IDs array

  UserIdsArray = []

  for ratingValue in extracted[1:]:
    if(Check_Exist_In_Array(UserIdsArray, ratingValue[0]) == False):
      UserIdsArray.append(ratingValue[0])

  print(UserIdsArray)
  print(len(UserIdsArray))

  #Create User IDs array

  ProductIdsArray = []

  for ratingValue in extracted[1:]:
    if(Check_Exist_In_Array(ProductIdsArray, ratingValue[1]) == False):
      ProductIdsArray.append(ratingValue[1])

  print(ProductIdsArray)
  print(len(ProductIdsArray))

  return Converted(UserIdsArray, ProductIdsArray, extracted), UserIdsArray, ProductIdsArray


def Data_Normilization(Converted):

    averagePointArray = [0] * 10
    sumArr = [0] * 10
    totalArr = [0] * 10

    x = 0
    for r in Converted:

        y = 0
        for c in r:

            if(c != 'x'):
                sumArr[y] += float(c)
                totalArr[y] += 1
            y += 1
        x += 1

        x = 0
        for value in totalArr:

            if (value != 0):
                averagePointArray[x] = sumArr[x] / totalArr[x]
            x += 1

    print(sumArr)
    print(totalArr)
    print(averagePointArray)

    A = np.array(Converted)

    B = np.array(averagePointArray)

    print(A)

    for xIndex, r in enumerate(Converted):
        for yIndex, c in enumerate(r):
            if (c != 'x'):
                Converted[xIndex][yIndex] = float(Converted[xIndex][yIndex]) - float(averagePointArray[yIndex])
            else:
                Converted[xIndex][yIndex] = 0

    C = np.array(Converted)

    print("Converted and normalized the results")
    print(C)

    return C


def Cosine_Fomular(x, y, Calculated_Matrix):
    row, col = Calculated_Matrix.shape

    # x.y

    multiply = 0

    for Index in range(row):
        multiply = multiply + \
            Calculated_Matrix[Index][x] * Calculated_Matrix[Index][y]

    if(DontShowDebug):
        print("x,y = ", x, y)
        print(multiply)

    # ||x||

    xVector = 0

    for Index in range(row):
        xVector = xVector + pow(Calculated_Matrix[Index][x], 2)

    if(DontShowDebug):
        print("X unsquared root results: ", xVector)

    xSqrt = math.sqrt(xVector)

    if(DontShowDebug):
        print("X squared: ", xSqrt)

    # ||y||

    yVector = 0

    for Index in range(row):
        yVector = yVector + pow(Calculated_Matrix[Index][y], 2)

    if(DontShowDebug):
        print("Y unsquared root results: ", yVector)

    ySqrt = math.sqrt(yVector)

    if(DontShowDebug):
        print("Y squared: ", ySqrt)

    # Cos(x,y) = x.y / ||x|| * ||y||

    Cosine = multiply / (xSqrt * ySqrt)

    if(DontShowDebug):
        print("Cosine result = ", Cosine)

    return Cosine


def Cosine_Similarity(Normalized_Matrix):
    row, col = Normalized_Matrix.shape

    Cosine = [[0 for i in range(col)] for j in range(col)]

    for xIndex, r in enumerate(Cosine):
        for yIndex, c in enumerate(r):
            Cosine[yIndex][xIndex] = Cosine_Fomular(
                xIndex, yIndex, Normalized_Matrix)

    toNpArray = np.array(Cosine)

    print("Result of similarity = ")

    resultFormalized = [[0 for i in range(col)] for j in range(col)]
    for xIndex, r in enumerate(toNpArray):
        for yIndex, c in enumerate(r):
            resultFormalized[yIndex][xIndex] = '{0:.10f}'.format(
                Cosine[yIndex][xIndex])

    ShowArray = np.array(resultFormalized)

    print(ShowArray)

    return toNpArray


def KNN_Calculate(K_Neighbors, Cosine_Similarity_Matrix, Normalized_Result_Matrix, Item_Index, User_Index, ProductIdsArray,UserIdsArray):
  
  #step 1

  UsersToCalculate = Normalized_Result_Matrix[Item_Index]

  #step 2

  Id_Array = []
  Value_Array = []


  for k in range(K_Neighbors):
    valueToAdd = -10000
    idToAdd = -1
    for Index, c in enumerate(UsersToCalculate):
      if ((Index != User_Index) & (valueToAdd < Cosine_Similarity_Matrix[User_Index][Index]) & IndexExist(Id_Array, Index) & (UsersToCalculate[Index] != 0)):
          valueToAdd = Cosine_Similarity_Matrix[User_Index][Index]
          idToAdd = Index
          
    if(idToAdd != -1):
      Value_Array.append(valueToAdd)
      Id_Array.append(idToAdd)

    tusoKnn = 0
    mausoKnn = 0 

    for Index, k in enumerate(Id_Array):
      tusoKnn += Value_Array[Index] * UsersToCalculate[k]
      mausoKnn += abs(Value_Array[Index])

    result = tusoKnn / mausoKnn
  return result


def Rating_Guessing_func(K_Neighbors, Cosine_Similarity_Matrix, Normalized_Result_Matrix, ProductIdsArray, UserIdsArray):
  print(ProductIdsArray)
  print(UserIdsArray)

  result_Matrix = Normalized_Result_Matrix

#Item = xIndex, User = yIndex

  for xIndex, r in enumerate(result_Matrix):
    for yIndex, c in enumerate(r): 
      if( c == 0 ):
        result_Matrix[xIndex][yIndex] = '{0:.10f}'.format(KNN_Calculate(K_Neighbors, Cosine_Similarity_Matrix, Normalized_Result_Matrix,xIndex ,yIndex, ProductIdsArray, UserIdsArray))

  return result_Matrix


def Export_dataframe_rating(dtframe):
    r_cols = [['UserId', 'RatedProductId', 'RatingScore']]
    for row in dtframe:
        r_cols.append([row[4], row[2], row[1]])

    getLogger().info(f'Export_dataframe_rating...{r_cols}')
    return r_cols


def Check_Exist_In_Array(Array, Value):
    for element in Array:
        if (element == Value):
            return True
    return False

def IndexExist(Array, Index):
    for x in Array: 
        if (x == Index):
            return False 
    return True