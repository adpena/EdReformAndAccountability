import pandas as pd
import csv
import os
import sys

sys.path.append("/Users/adpena/PycharmProjects/CharterCostTracker/")

import utils


def gen_tapr_student_legend():
    tapr_student_legend_path = "/Users/adpena/PycharmProjects/RespectCampaign/TAPR header labels_students information - Sheet1.csv"

    tapr_student_directory = ""

    tapr_student_legend = {}

    with open(tapr_student_legend_path, "r") as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:

            tapr_student_legend[row[0]] = row[3]

    # print(tapr_student_legend)
    return tapr_student_legend


def get_tapr_student_stats(district_number, school_year):
    school_year_start = school_year.split("-")[0]
    school_year_end = school_year.split("-")[1]

    student_data_path = f"/Users/adpena/PycharmProjects/RespectCampaign/TAPR district student information reports/DSTUD_{school_year_start}_{school_year_end[2:]}.csv"

    legend = gen_tapr_student_legend()

    district_number = utils.pad_district_number(district_number)

    for k, v in legend.items():
        if "2021" in v:
            v = v.replace("District 2021 ", "").replace("2021", "")
            legend[k] = v
        if "2022" in v:
            v = v.replace("District 2022 ", "")
            legend[k] = v

    student_attrition_mobility = [
        # "DPEMBLAP",
        # "DPETATTP",
        "DPEMALLP",
        # "DPEMECOP",
        # "DPEMSPEP",
    ]

    student_demographics = [
        "DPETALLC",
        "DPETBLAP",
        "DPETRSKP",
        # "DPETSAUP",
        # "DPETSBHP",
        # "DPETDSLP",
        "DPETECOP",
        # "DPETSINP",
        # "DPETSPHP",
        # "DPET504P",
        "DPETSPEP",
        # "DPETTT1P",
        # "DPETSIMC",
    ]

    filters = [
        ["DISTRICT"],
        # retention,
        # class_size,
        student_attrition_mobility,
        student_demographics,
    ]

    final_legend = {}

    for k, v in legend.items():
        for filter_list in filters:
            if k in filter_list:
                final_legend[k] = v.replace("2021", school_year_start).replace("2022", school_year_end)

    df = pd.read_csv(student_data_path)

    df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

    # print(list(df.columns))

    # Flatten the nested list into a single list
    final_cols = [element for sublist in filters for element in sublist]

    df = df[final_cols]

    df = df.rename(columns=final_legend)

    # print(df.head())

    row = df[df['District Number'] == district_number]

    # If there is more than one row with the same district_number,
    # this will convert all of them into a list of dictionaries.
    # If you only want the first one, you can use row.iloc[0].to_dict() instead.
    result = row.to_dict('records')

    # print(result)

    return result[0]


def get_tapr_staar_data(district_number, school_year):

    district_number = utils.pad_district_number(district_number)

    if school_year in ["2019-2020", "2020-2021", "2021-2022"]:

        df = pd.read_csv(f"TAPR STAAR data/DSTAAR_ALL_{school_year.split('-')[0]}_{school_year.split('-')[1][2:]}.csv")

        df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

        df = df[df["DISTRICT"] == district_number]

        # all students math = DDA00AM01222R in 2021-2022 (DISTRICT 2022); DDA00AM01221R in 2020-2021
        # Get list of columns that contain 'DDA00AM012'

        # reading = DDA00AM01222R in 2021-2022
        math_cols = [col for col in df.columns if 'DDA00AM012' in col]

        # If there are any matching columns, return the value in the first one.
        # print(len(math_cols), ": MATH COLS")
        if math_cols:
            math = df[math_cols[0]].values[0]
        else:
            math = None

        reading_cols = [col for col in df.columns if 'DDA00AR012' in col]

        # If there are any matching columns, return the value in the first one.
        if reading_cols:
            reading = df[reading_cols[0]].values[0]
        else:
            reading = None

        label = f"District {school_year.split('-')[0]} Domain 1A: Meets Grade Level STD, Summed Grades 3-12, All Students Mathematics Rate"

        return {"MATH, MEETS STANDARD: ALL TESTED STUDENTS": math,
                "READING, MEETS STANDARD: ALL TESTED STUDENTS": reading,
                "LABEL": label, "DIST NUM": district_number}

    elif school_year in ["2017-2018", "2018-2019"]:
        # math = DDA00AM01219R in 2018-2019
        # reading = DDA00AR01219R

        df = pd.read_csv(f"TAPR STAAR data/DSTAAR_ALL_{school_year.split('-')[0]}b.csv")

        df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

        df = df[df["DISTRICT"] == district_number]

        math_cols = [col for col in df.columns if 'DDA00AM012' in col]

        # If there are any matching columns, return the value in the first one.
        # print(len(math_cols), ": MATH COLS")
        if math_cols:
            math = df[math_cols[0]].values[0]
        else:
            math = None

        reading_cols = [col for col in df.columns if 'DDA00AR012' in col]

        # If there are any matching columns, return the value in the first one.
        if reading_cols:
            reading = df[reading_cols[0]].values[0]
        else:
            reading = None

        label = {
            "2017-2018": "District 2017 Domain 1A: Meets Grade Level STD, Summed Grades 3-12, All Students [Subject] Rate",
            "2018-2019": "District 2018 Domain 1A: Meets Grade Level STD, Summed Grades 3-12, All Students [Subject] Rate",
        }
        label = label[school_year]

        return {"MATH, MEETS STANDARD: ALL TESTED STUDENTS": math,
                "READING, MEETS STANDARD: ALL TESTED STUDENTS": reading,
                "LABEL": label, "DIST NUM": district_number}


    elif school_year in ["2016-2017"]:
        # CONFIRM THAT 2016-2017 uses the same label; which columns should I put these into?
        # ALL GRADES % MEET GRADE LEVEL: MATH, ALL GRADES % MEET GRADE LEVEL: READING; asterisk years not available 2011-2012 is one

        # 2016-2017 math rate = DA00AM04216R, reading = DA00AR04216R

        df = pd.read_csv(f"TAPR STAAR data/DSTAAR_ALL_{school_year.split('-')[0]}_{school_year.split('-')[1][2:]}_MEETS.csv")

        df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

        df = df[df["DISTRICT"] == district_number]

        math_cols = [col for col in df.columns if 'DA00AM04216R' in col]

        # If there are any matching columns, return the value in the first one.
        # print(len(math_cols), ": MATH COLS")
        if math_cols:
            math = df[math_cols[0]].values[0]
        else:
            math = None

        reading_cols = [col for col in df.columns if 'DA00AR04216R' in col]

        # If there are any matching columns, return the value in the first one.
        if reading_cols:
            reading = df[reading_cols[0]].values[0]
        else:
            reading = None

        label = "District 2016 STAAR Meets Grade Level: Rate of students meeting Grade Level Standard requirement for [Subject] - All Rate"

        return {"MATH, MEETS STANDARD: ALL TESTED STUDENTS": math,
                "READING, MEETS STANDARD: ALL TESTED STUDENTS": reading,
                "LABEL": label, "DIST NUM": district_number}

    elif school_year in ["2013-2014", "2014-2015", "2015-2016"]:

        df = pd.read_csv(f"TAPR STAAR data/DSTAAR_ALL_{school_year.split('-')[0]}_{school_year.split('-')[1][2:]}_STANDARD.csv")

        df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

        df = df[df["DISTRICT"] == district_number]

        math_cols = [col for col in df.columns if 'DA00AM01S' in col]

        # If there are any matching columns, return the value in the first one.
        # print(len(math_cols), ": MATH COLS")
        if math_cols:
            math = df[math_cols[0]].values[0]
        else:
            math = None

        reading_cols = [col for col in df.columns if 'DA00AR01S' in col]

        # If there are any matching columns, return the value in the first one.
        if reading_cols:
            reading = df[reading_cols[0]].values[0]
        else:
            reading = None

        label = {
            "2013-2014": "District 2014 Index 1: Index 1 (Phase 1 Level 2 & PM_ELL), Summed Grades 3-11, All Students [Subject] Rate",
            "2014-2015": "District 2015 Index 1: Index 1 (Phase1 Level2 & PM_ELL), Summed Grades 3-11, All Students [Subject] Rate",
            "2015-2016": "District 2016 Index 1: Index 1 (Phase-in Level II & PM_ELL), Summed Grades 3-11, All Students [Subject] Rate",
        }
        label = label[school_year]

        return {"MATH, MEETS STANDARD: ALL TESTED STUDENTS": math,
                "READING, MEETS STANDARD: ALL TESTED STUDENTS": reading,
                "LABEL": label, "DIST NUM": district_number}

    elif school_year in ["2012-2013"]:
        # District 2012 math = DA00AM01512R, reading = DA00AR01512R

        df = pd.read_csv(
            f"TAPR STAAR data/DSTAAR_ALL_{school_year.split('-')[0]}_{school_year.split('-')[1][2:]}_STANDARD.csv")

        df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

        df = df[df["DISTRICT"] == district_number]

        math_cols = [col for col in df.columns if 'DA00AM01512R' in col]

        # If there are any matching columns, return the value in the first one.
        # print(len(math_cols), ": MATH COLS")
        if math_cols:
            math = df[math_cols[0]].values[0]
        else:
            math = None

        reading_cols = [col for col in df.columns if 'DA00AR01512R' in col]

        # If there are any matching columns, return the value in the first one.
        if reading_cols:
            reading = df[reading_cols[0]].values[0]
        else:
            reading = None

        label = "DISTRICT 2012 Grade All [Subject] Total All Students, % Met Level 2 Phase-in (Rate)"

        return {"MATH, MEETS STANDARD: ALL TESTED STUDENTS": math,
                "READING, MEETS STANDARD: ALL TESTED STUDENTS": reading,
                "LABEL": label, "DIST NUM": district_number}

    elif school_year in ["2011-2012"]:
        # District 2012 math = DA311TM12R, reading = DA311TR12R

        df = pd.read_csv(
            f"TAPR STAAR data/DTAKS_ALL_{school_year.split('-')[0]}_{school_year.split('-')[1][2:]}_STANDARD.csv")

        df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

        df = df[df["DISTRICT"] == district_number]

        math_cols = [col for col in df.columns if 'DA311TM12R' in col]

        # If there are any matching columns, return the value in the first one.
        # print(len(math_cols), ": MATH COLS")
        if math_cols:
            math = df[math_cols[0]].values[0]
        else:
            math = None

        reading_cols = [col for col in df.columns if 'DA311TR12R' in col]

        # If there are any matching columns, return the value in the first one.
        if reading_cols:
            reading = df[reading_cols[0]].values[0]
        else:
            reading = None

        label = "District 2012 TAKS - TAKS Met Standard: Grades 10-11, Summed All Students [Subject] Rate"

        return {"MATH, MEETS STANDARD: ALL TESTED STUDENTS": math,
                "READING, MEETS STANDARD: ALL TESTED STUDENTS": reading,
                "LABEL": label, "DIST NUM": district_number}

    elif school_year in ["2009-2010", "2010-2011"]:
        df = pd.read_csv(
            f"TAPR STAAR data/DTAKS_ALL_{school_year.split('-')[0]}_{school_year.split('-')[1][2:]}_STANDARD.csv")

        df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

        df = df[df["DISTRICT"] == district_number]

        math_cols = [col for col in df.columns if f'DA311TM{school_year.split("-")[1][2:]}' in col]

        # If there are any matching columns, return the value in the first one.
        # print(len(math_cols), ": MATH COLS")
        if math_cols:
            math = df[math_cols[0]].values[0]
        else:
            math = None

        reading_cols = [col for col in df.columns if f'DA311TR{school_year.split("-")[1][2:]}' in col]

        # If there are any matching columns, return the value in the first one.
        if reading_cols:
            reading = df[reading_cols[0]].values[0]
        else:
            reading = None

        label = {
            "2009-2010": "District 2010 TAKS - Accountability Test: Grades 3-11, Summed All Students [Subject] Rate",
            "2010-2011": "District 2011 TAKS - Accountability Test: Grades 3-11, Summed All Students [Subject] Rate",
        }
        label = label[school_year]

        return {"MATH, MEETS STANDARD: ALL TESTED STUDENTS": math,
                "READING, MEETS STANDARD: ALL TESTED STUDENTS": reading,
                "LABEL": label, "DIST NUM": district_number}


print(" ")

"""staar_data = []
for sy in list([f"{x}-{x+1}" for x in range(2009, 2022)]):
    staar_data.append(get_tapr_staar_data('101912', sy))


student_stats = []
for sy in list([f"{x}-{x+1}" for x in range(2011, 2022)]):
    student_stats.append(get_tapr_student_stats('101912', sy))

# Get the keys (column labels) from the first dictionary in the list
keys = staar_data[0].keys()

with open('staar data_Houston ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(staar_data)

# Get the keys (column labels) from the first dictionary in the list
keys = student_stats[0].keys()

with open('student stats_Houston ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(student_stats)



staar_data = []
for sy in list([f"{x}-{x+1}" for x in range(2009, 2022)]):
    staar_data.append(get_tapr_staar_data('057905', sy))


student_stats = []
for sy in list([f"{x}-{x+1}" for x in range(2011, 2022)]):
    student_stats.append(get_tapr_student_stats('057905', sy))

# Get the keys (column labels) from the first dictionary in the list
keys = staar_data[0].keys()

with open('staar data_Dallas ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(staar_data)

# Get the keys (column labels) from the first dictionary in the list
keys = student_stats[0].keys()

with open('student stats_Dallas ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(student_stats)"""


def get_number_of_low_performing_campuses(district_number, school_year, prev_unacceptable_campuses):

    district_number = utils.pad_district_number(district_number)

    testing_year = school_year.split("-")[1]

    df = pd.read_excel("multi-year_accountability_rating_list_2022.xlsx")

    df.columns = [col.replace("\n", " ") for col in df.columns]

    df["Campus Number"] = df["Campus Number"].apply(lambda x: "'" + ("0" * (9 - len(str(x)))) + str(x))
    df["District Number"] = df["Campus Number"].apply(lambda x: x[0:7])

    unacceptable = {
        2011: ['Academically Unacceptable','AEA: Academically Unacceptable'],
        2012: [],
        2013: ['Improvement Required'],
        2014: ['Improvement Required'],
        2015: ['Improvement Required'],
        2016: ['Improvement Required'],
        2017: ['Improvement Required'],
        2018: ['Improvement Required'],
        2019: ["D", "F"],
        2020: [],
        2021: [],
        2022: ["Not Rated: Senate Bill 1365"],
    }

    year_was_rated = len(unacceptable[int(testing_year)]) > 0

    unacceptable_ratings = []

    for year, ratings in unacceptable.items():
        for rating in ratings:
            if rating not in unacceptable_ratings:
                unacceptable_ratings.append(rating)

    column_label = f"Campus {testing_year} Rating"

    filtered_rows = df[(df[column_label].isin(unacceptable_ratings)) & (df['District Number'] == district_number)]
    num_rows = len(filtered_rows)

    current_unacceptable_campuses = set(filtered_rows['Campus Number'])
    new_campuses = len(current_unacceptable_campuses - prev_unacceptable_campuses)
    old_campuses = len(prev_unacceptable_campuses - current_unacceptable_campuses)

    return ({"DIST NUM": district_number, "LOW-PERFORMING CAMPUSES": num_rows, "NEW LOW-PERFORMING CAMPUSES": new_campuses, "DISCONTINUED LOW-PERFORMING CAMPUSES": old_campuses},
            current_unacceptable_campuses,
            year_was_rated)


"""low_performing_campuses_data = []
prev_unacceptable_campuses = set()
for sy in list([f"{x}-{x+1}" for x in range(2010, 2022)]):
    data, current_unacceptable_campuses, year_was_rated = get_number_of_low_performing_campuses('057905', sy, prev_unacceptable_campuses)
    low_performing_campuses_data.append(data)
    if year_was_rated:
        prev_unacceptable_campuses = current_unacceptable_campuses

keys = low_performing_campuses_data[0].keys()

with open('low-performing campuses data_Dallas ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(low_performing_campuses_data)

low_performing_campuses_data = []
prev_unacceptable_campuses = set()
for sy in list([f"{x}-{x + 1}" for x in range(2010, 2022)]):
    data, current_unacceptable_campuses, year_was_rated = get_number_of_low_performing_campuses('101912', sy,
                                                                                                prev_unacceptable_campuses)
    low_performing_campuses_data.append(data)
    if year_was_rated:
        prev_unacceptable_campuses = current_unacceptable_campuses

keys = low_performing_campuses_data[0].keys()

with open('low-performing campuses data_Houston ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(low_performing_campuses_data)"""


def get_annual_dropout_data(district_number, school_year):
    district_number = utils.pad_district_number(district_number)

    school_year_new = f"{int(school_year.split('-')[0]) - 1}-{int(school_year.split('-')[1]) - 1}"

    school_year_start = school_year_new.split("-")[0]

    school_year_end = school_year_new.split("-")[1]

    dropout_data_paths = {
        "2009-2010": "TAPR Annual Dropout data/dothr_2009_10.csv",
        "2010-2011": "TAPR Annual Dropout data/dothr_2010_11.csv",
        "2011-2012": "TAPR Annual Dropout data/dothr_2011_12.csv",
        "2012-2013": "TAPR Annual Dropout data/DOTHR_2012_13.csv",
        "2013-2014": "TAPR Annual Dropout data/DOTHR_2013_14.csv",
        "2014-2015": "TAPR Annual Dropout data/DOTHR_2014_15.csv",
        "2015-2016": "TAPR Annual Dropout data/DOTHR_2015_16.csv",
        "2016-2017": "TAPR Annual Dropout data/DOTHR_2016_17.csv",
        "2017-2018": "TAPR Annual Dropout data/DDROP_ATT_2017_18.csv",
        "2018-2019": "TAPR Annual Dropout data/DDROP_ATT_2018_19.csv",
        "2019-2020": "TAPR Annual Dropout data/DDROP_ATT_2019_20.csv",
        "2020-2021": "TAPR Annual Dropout data/DDROP_ATT_2020_21.csv",
        "2021-2022": "TAPR Annual Dropout data/DDROP_ATT_2021_22.csv",
    }

    df = pd.read_csv(dropout_data_paths[school_year])

    df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

    df = df[df["DISTRICT"] == district_number]

    if school_year not in ["2011-2012"]:
        cols_of_interest = {
            "DISTRICT": "District Number",
            # Dropout Y1 7-8
            f"DA0708DR{school_year_start[2:]}R": f"District Prior SY Y1 Annual Dropout for Grades 07-08: All Students Rate",
            # Dropout Y2 7-8
            f"DA0708DR{school_year_end[2:]}R": f"District Prior SY Y2 Annual Dropout for Grades 07-08: All Students Rate",
            # Dropout Y1 9-12
            f"DA0912DR{school_year_start[2:]}R": f"District Prior SY Y1 Annual Dropout for Grades 09-12: All Students Rate",
            # Dropout Y2 9-12
            f"DA0912DR{school_year_end[2:]}R": f"District Prior SY Y2 Annual Dropout for Grades 09-12: All Students Rate",

        }
    else:
        print("WEIRD SY:", school_year)
        cols_of_interest = {
            "DISTRICT": "District Number",
            # Dropout Y2 7-8
            f"DA0708DR{school_year_end[2:]}R": f"District Prior SY Y2 Annual Dropout for Grades 07-08: All Students Rate",
            # Dropout Y2 9-12
            f"DA0912DR{school_year_end[2:]}R": f"District Prior SY Y2 Annual Dropout for Grades 09-12: All Students Rate",

        }

    df = df.rename(columns=cols_of_interest)

    df = df[[x for x in list(cols_of_interest.values())]]

    return df.to_dict('records')[0]


"""annual_dropout_data = []
for sy in list([f"{x}-{x+1}" for x in range(2009, 2022)]):
    try:
        annual_dropout_data.append(get_annual_dropout_data('101912', sy))
    except Exception as e:
        print(sy, e)
        exit()

# Get the keys (column labels) from the first dictionary in the list
keys = annual_dropout_data[0].keys()

with open('annual dropout data_Houston ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(annual_dropout_data)


annual_dropout_data = []
for sy in list([f"{x}-{x+1}" for x in range(2009, 2022)]):
    annual_dropout_data.append(get_annual_dropout_data('057905', sy))

# Get the keys (column labels) from the first dictionary in the list
keys = annual_dropout_data[0].keys()

with open('annual dropout data_Dallas ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(annual_dropout_data)"""


def get_instructional_expenditures_ratio(district_number, school_year):

    district_number = utils.pad_district_number(district_number)

    col_label = {
        "DISTRICT": "District Number",
        "DPFEIERP": f"SY Y1 Finance: Instructional Expenditures Ratio"
    }

    df = pd.read_csv(f"/Users/adpena/PycharmProjects/RespectCampaign/TAPR district staff information reports/{school_year} TAPR staff data.csv" if school_year not in ["2009-2010", "2010-2011", "2011-2012"] else f"/Users/adpena/PycharmProjects/RespectCampaign/TAPR district staff information reports/{school_year} AEIS staff data.csv")

    df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

    df = df[df["DISTRICT"] == district_number]

    # print(df.columns)

    df = df[[x for x in list(col_label.keys())]]

    df = df.rename(columns=col_label)

    return df.to_dict('records')[0]


"""print(get_instructional_expenditures_ratio('057905', "2021-2022"))

ie_ratio_data = []
for sy in list([f"{x}-{x+1}" for x in range(2009, 2022)]):
    try:
        ie_ratio_data.append(get_instructional_expenditures_ratio('101912', sy))
    except Exception as e:
        print(sy, e)
        ie_ratio_data.append({"District Number": "'101912", 'SY Y1 Finance: Instructional Expenditures Ratio': None})

# Get the keys (column labels) from the first dictionary in the list
keys = ie_ratio_data[0].keys()

with open('IE ratio data_Houston ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(ie_ratio_data)


ie_ratio_data = []
for sy in list([f"{x}-{x+1}" for x in range(2009, 2022)]):
    try:
        ie_ratio_data.append(get_instructional_expenditures_ratio('057905', sy))
    except Exception as e:
        print(sy, e)
        ie_ratio_data.append({"District Number": "'057905", 'SY Y1 Finance: Instructional Expenditures Ratio': None})

# Get the keys (column labels) from the first dictionary in the list
keys = ie_ratio_data[0].keys()

with open('IE ratio data_Dallas ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(ie_ratio_data)"""


def get_student_attrition_rate(district_number, school_year):
    district_number = utils.pad_district_number(district_number)

    school_year_start = school_year.split("-")[0]
    school_year_end = school_year.split("-")[1]

    student_data_path = f"/Users/adpena/PycharmProjects/RespectCampaign/TAPR district student information reports/DSTUD_{school_year_start}_{school_year_end[2:]}.csv"

    df = pd.read_csv(student_data_path)

    print(list(df.columns))

    df["DISTRICT"] = df["DISTRICT"].apply(utils.pad_district_number)

    df = df[df["DISTRICT"] == district_number]

    df = df[["DISTRICT", "DPETATTP"]]

    df = df.rename(columns={
        "DISTRICT": "District Number",
        "DPETATTP": "Student Attrition Rate",
    })

    return df.to_dict('records')[0]


student_attrition_data = []
for sy in list([f"{x}-{x+1}" for x in range(2009, 2022)]):
    try:
        student_attrition_data.append(get_student_attrition_rate('101912', sy))
    except Exception as e:
        print(sy, e)
        student_attrition_data.append({"District Number": "'101912", 'Student Attrition Rate': None})

# Get the keys (column labels) from the first dictionary in the list
keys = student_attrition_data[0].keys()

with open('student attrition data_Houston ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(student_attrition_data)


student_attrition_data = []
for sy in list([f"{x}-{x+1}" for x in range(2009, 2022)]):
    try:
        student_attrition_data.append(get_student_attrition_rate('057905', sy))
    except Exception as e:
        print(sy, e)
        student_attrition_data.append({"District Number": "'057905", 'Student Attrition Rate': None})

# Get the keys (column labels) from the first dictionary in the list
keys = student_attrition_data[0].keys()

with open('student attrition data_Dallas ISD.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(student_attrition_data)
