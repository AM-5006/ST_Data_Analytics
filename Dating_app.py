import pandas as pd
import datetime
import re

def feet_to_centi(i):
    feet, inches = re.findall(pattern, i)[0]
    height_cm = int(feet) * 30.48 + int(inches or 0) * 2.54
    return height_cm

def calculate_age(DOB):
    age = []
    for i in DOB:
        d = i.split('/')
        d[2] = '19' + d[2]
        date = datetime.datetime.strptime('-'.join(d), '%m-%d-%Y').date()
        years = (datetime.date.today() - date).days/365.25
        age.append(int(years))
    return age

def Filter(first_name, last_name):
    female = df_female[(df_female["First Name"]==first_name) & (df_female["Last Name"]==last_name)]
    print(f'\nFemale details:\n{female}\n')
    try:
        Age = int(female["Age"])
        Height = int(female["Height"])
        Community_Preference = str(female["Community Preference"]).strip(str(female.index)).strip().split()[0]
        Religion = str(female["Religion"]).strip(str(female.index)).strip(' ').split()[0]
        result = df_male[(df_male["Age"] > Age) & (df_male["Height"] > Height) &(df_male["Community Preference"] == Community_Preference) & (df_male["Religion"] == Religion)]
        return result
    except Exception as e:
        return None


if __name__=='__main__':
    df = pd.read_csv("Python Intership Assignment - Data.csv")
    pattern = r"(\d+)(?:\.|ft |\'| ft |feet )?(\d+)?(?:\"| in|inch| cm)?"

    df["Height"] = df["Height"].apply(feet_to_centi)
    df["Age"] = calculate_age(df["Date of Birth"])

    df_male = df[df["Gender"]=="Male"]
    df_female = df[df["Gender"]=="Female"]


    FN = input("Enter the first name: ")
    LN = input("Enter the last name: ")

    result = Filter(FN, LN)
    if result.empty: 
        print("No match found")
    elif result is None:
        print("Error")
    else:
        print(f'\nMatching Profiles:\n {result}')
        result.to_csv(f'Matching_for_{FN}_{LN}.csv', index=False)

