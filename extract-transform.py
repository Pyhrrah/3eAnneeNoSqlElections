# ETL -> Extract Transform Load

# activation de l'environnement virtuel
# py -m venv .venv
# .venv\Scripts\activate

# Travailler sur le groupe 3 de département


import pandas as pd
import numpy as np
import matplotlib as plt

def convertXLStoCSV(filenameIn : str, filenameOut : str) :
    temp = pd.read_excel(filenameIn)
    temp.to_csv(filenameOut)

# convertXLStoCDV("MDB-INSEE-V2.xls","insee_communes.csv")

## Script fourni par le professeur pour mettre en forme les données

import pandas as pd
from csv import QUOTE_NONNUMERIC

dept = '03'

df_regions = pd.read_csv('data/regions-france.csv', sep=",", dtype=str)
df_regions.to_csv(f'clean/{dept}-regions.csv', sep=",", index=False, quoting=QUOTE_NONNUMERIC)

df_deps = pd.read_csv('data/departements-france.csv', sep=",", dtype=str)
df_deps['code_departement'] = df_deps['code_departement'].str.zfill(2)
df_deps.to_csv(f'clean/{dept}-departements.csv', sep=",", index=False, quoting=QUOTE_NONNUMERIC)

df_communes = pd.read_csv(
    'data/communes.csv', sep=",",
    dtype={'code_commune_INSEE': str, 'code_departement': str, 'code_region': str}
    )

df_communes['code_commune_INSEE'] = df_communes['code_commune_INSEE'].str.zfill(5)
df_communes['code_departement'] = df_communes['code_departement'].str.zfill(2)
df_communes['code_region'] = df_communes['code_region'].str.zfill(2)

df_communes = df_communes[['code_commune_INSEE', 'nom_commune', 'latitude', 'longitude', 'code_departement', 'code_region']]
df_communes = df_communes[df_communes['code_departement'] == dept]
df_communes = df_communes.drop_duplicates(subset='code_commune_INSEE')

df_communes.to_csv(f'clean/{dept}-communes.csv', sep=",", index=False, quoting=QUOTE_NONNUMERIC)

df_candidats = pd.read_csv('data/candidats-2026.csv', sep=";", dtype={'Code département': str, 'Code circonscription': str, 'CC': str})
df_candidats['Code département'] = df_candidats['Code département'].str.zfill(2)
df_candidats['Code circonscription'] = df_candidats['Code circonscription'].str.zfill(5)

df_candidats = df_candidats[df_candidats['Code département'] == dept]
df_candidats = df_candidats[df_candidats['Tête de liste'] == 'OUI']
df_candidats.to_csv(f'clean/{dept}-candidats.csv', sep=",", index=False, quoting=QUOTE_NONNUMERIC)

df_insee = pd.read_csv('data/insee_communes.csv', sep=",", dtype={'CODGEO': str, 'REG': str, 'DEP': str})
df_insee['DEP'] = df_insee['DEP'].str.zfill(2)
df_insee['REG'] = df_insee['REG'].str.zfill(2)
df_insee['CODGEO'] = df_insee['CODGEO'].str.zfill(5)
df_insee = df_insee[df_insee['DEP'] == dept]
df_insee.to_csv(f'clean/{dept}-insee.csv', sep=",", index=False, quoting=QUOTE_NONNUMERIC)

