import pandas as pd
import numpy as np
import matplotlib as plt

def convertXLStoCsv(filenameIn : str, filenameOut : str) :
    temp = pd.read_excel(filenameIn)
    temp.to_csv(filenameOut)

# convertXLStoCsv("MDB-INSEE-V2.xls","insee_communes.csv")