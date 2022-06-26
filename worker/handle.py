import numpy as np
import pandas as pandas
import csv as csv
import math as math
import requests
import json
import time
from logger import getLogger
from dotenv import dotenv_values

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
    recommendation(fo)

    # SEED handle. Sleep 3s send notification to asp.net hook
    url = WEB_HOOK

    payload = json.dumps({
        "data": [1, 2, 3]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        # Nếu xịn hơn  thì nên tách cái lỗi này để có thể retry lại nếu mà server bên ASP.net bị tạch :V
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

    getLogger().info(f'Rows...{rows}')

    # header
    something = get_datafarame_ratings_base(upload, header)

    Extracted = Export_dataframe_rating(something)

    Converted = Convert_DTFrame(Extracted)

    Normalized = Data_Normilization(Converted)

    getLogger().info(f'Normalized...{Normalized}')

    resultOfSimilarity = Cosine_Similarity(Normalized)

    Rating_Guessing_func(K_neighbors_values, resultOfSimilarity, Normalized)

    getLogger().info(f'Normalized2...{Normalized}')


def get_datafarame_ratings_base(text, header):

    ratings = pandas.read_csv(text ,sep=',', names=header)

    print(ratings)

    Y_data = ratings.values

    return Y_data


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

    # Create User IDs array

    UserIdsArray = []

    for ratingValue in extracted[1:]:
        if(Check_Exist_In_Array(UserIdsArray, ratingValue[0]) == False):
            UserIdsArray.append(ratingValue[0])

    print(UserIdsArray)
    print(len(UserIdsArray))

    # Create User IDs array

    ProductIdsArray = []

    for ratingValue in extracted[1:]:
        if(Check_Exist_In_Array(ProductIdsArray, ratingValue[1]) == False):
            ProductIdsArray.append(ratingValue[1])

    print(ProductIdsArray)
    print(len(ProductIdsArray))

    return Converted(UserIdsArray, ProductIdsArray, extracted)


def Data_Normilization(Converted):

    averagePointArray = [0] * 10
    sumArr = [0] * 10
    totalArr = [0] * 10

    x = 0
    for r in Converted:

        y = 0
        for c in r:

            if(c != 'x'):
                sumArr[y] += c
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
                Converted[xIndex][yIndex] = Converted[xIndex][yIndex] - \
                    averagePointArray[yIndex]
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


def KNN_Calculate(K_Neighbors):
    return 1


def Rating_Guessing_func(K_Neighbors, Cosine_Similarity_Matrix, Normalized_Result_Matrix):

    result_Matrix = Normalized_Result_Matrix

    for xIndex, r in enumerate(result_Matrix):
        for yIndex, c in enumerate(r):
            if(c == 0):
                result_Matrix[xIndex][yIndex] = KNN_Calculate(K_Neighbors)

    print(result_Matrix)
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
