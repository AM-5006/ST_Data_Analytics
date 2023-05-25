import pandas as pd
import Levenshtein
from openpyxl import Workbook
import re
import datetime

def feet_to_centi(height):
    try:
        pattern = r"(\d+)(?:'| ft ) (\d+)\""
        matches = re.match(pattern, height)
        if matches is None:
            # raise ValueError(f"Invalid height format: {height}")
            return None
        feet = int(matches.group(1))
        inches = int(matches.group(2))
        total_inches = feet * 12 + inches
        centimeters = total_inches * 2.54
        return centimeters
    except Exception as e:
        # print(e)
        return None

def calculate_age(DOB):
    try:
        age = []
        for i in DOB:
            try:
                date = datetime.datetime.strptime(i,'%d-%b-%y').date()
                years = (datetime.date.today() - date).days/365.25
                age.append(int(years))
            except Exception as e:
                age.append(None)
        return age
    except Exception as e:
        # print(e)
        return None

#checks if a there is a small difference between community names. High probability that the community names are same if the difference is small
def cleansing_community(community):  
    threshold = 2
    result = []
    for i in range(len(community)):
        for j in range(i+1, len(community)):
            c1 = community[i]
            c2 = community[j]

            distance = Levenshtein.distance(c1.lower(), c2.lower())
            if (abs(len(c1)-len(c2))<=1 and sum(a.lower()!=b.lower() for a, b in zip(c1,c2)) == 1) or (abs(distance) <= threshold):
                result.append((c1, c2))
    return result

def get_status(female_fname, female_lname, male_fname, male_lname, community_name):
    try:
        status_df = pd.read_excel('Community_status.xlsx', sheet_name=community_name.upper())
        row_index = status_df.index[(status_df['First Name'] == female_fname) & (status_df['Last Name'] == female_lname)].tolist()[0]
        sliced_df = status_df.iloc[row_index+2:]
        for index, row in sliced_df.iterrows():
            if row.isna().all():
                return None
            if row["First Name"] == male_fname and row["Last Name"] == male_lname:
                return row["Status"]
    except Exception as e:
        # print(e)
        return None


def matching(male_df, female, community_name):
    try:
        Age = female["Age"]
        Height = female["Height"]
        # Caste_Preference = female["Caste Preference"]

        if pd.notna(Age) and pd.notna(Height): 
            result = male_df[(male_df["Age"] > Age) & (male_df["Height"] > Height)]
            status_col = ["NA", ""]
            for index, row in result.iterrows():
                status = get_status(female["First Name"], female["Last Name"], row["First Name"], row["Last Name"], community_name)
                status_col.append(status)
            return (result, status_col)
        else:
            return (None, None)
    except Exception as e:
        print(e)
        return (None, None)

if __name__=='__main__':
    df = pd.read_csv("Data.csv")

    df["Height"] = df["Height"].apply(feet_to_centi)
    df["Age"] = calculate_age(df["Date of Birth"])
    
    community = list(df["Community"].unique())
    similar_community = cleansing_community(community)
    
    for i in range(len(similar_community)):
        c1 = df[df['Community'] == similar_community[i][0]].shape[0]
        c2 = df[df['Community'] == similar_community[i][1]].shape[0]
        if c1>c2:
            df['Community'] = df['Community'].replace([similar_community[i][1], similar_community[i][0]], similar_community[i][0])
        else:
            df['Community'] = df['Community'].replace([similar_community[i][0], similar_community[i][1]], similar_community[i][1])
    
    df['Community'] = df['Community'].str.upper()
    df['Caste Preference'] = df['Caste Preference'].str.upper()

    for i in df['Community'].unique():
        community_df = df[(df["Community"] == i)]
        male_df = pd.DataFrame(community_df[(community_df["Gender"] == "Male")])
        female_df = community_df[(community_df["Gender"] == "Female")]
        try:
            writer = pd.ExcelWriter(f'Output/{i}.xlsx', engine ='openpyxl')
            community_df.to_excel(writer, sheet_name=i, index=False)
            male_df.to_excel(writer, sheet_name=(i+"-Male"), index = False)
            female_df.to_excel(writer, sheet_name=(i+"-Female"), index = False)
            k = 0
            for index, row in female_df.iterrows():
                result = pd.DataFrame()
                result = result.append(row, ignore_index=True)

                empty_row = pd.Series({}, dtype=object)
                result = result.append(empty_row, ignore_index=True)

                matched_df, status_col = matching(male_df, row, i) 
                result = result.append(matched_df, ignore_index=True)
                result["Status"] = status_col

                result.to_excel(writer, sheet_name=(f'{k}_{row["First Name"]}_{row["Last Name"]}'), index=False)
                k += 1
        except Exception as e:
            print(e) 
        finally:
            writer.save()


