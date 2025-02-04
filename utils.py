import numpy as np

lengths = [5, 12, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 10]  # lengths of intervals to split rows in
irrigation = np.genfromtxt('./structures_files/irrigation.txt',dtype='str')

def search_string_in_file(file_name, string_to_search):
    """Search for the given string in file and return the line numbers containing that string"""
    line_number = 0
    list_of_results = []
    # Open the file in read only mode
    with open(file_name, 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            line_number += 1
            if string_to_search in line:
                # If yes, then add the line number & line as a tuple in the list
                list_of_results.append(line_number)
    # Return list of tuples containing line numbers and lines where string is found
    return list_of_results

def writenewIWR(scenario, all_split_data, all_data, firstline_iwr, i, users,
                curtailment_per_user, general_curtailment, curtailment_years):
    # replace former iwr demands with new
    new_data = []
    for j in range(len(all_split_data) - firstline_iwr):
        row_data = []
        # split first 3 columns of row on space and find 1st month's flow
        row_data.extend(all_split_data[j + firstline_iwr][0].split())
        # check if year is a curtailment year and if user is to be curtailed
        if int(row_data[0]) in curtailment_years and row_data[1] in users:
            index = np.where(users == row_data[1])[0][0]
            remaining_demand = 1 - (curtailment_per_user[index] * (100 - general_curtailment) / 100)
            # scale first month
            value = float(row_data[2]) * remaining_demand
            row_data[2] = str(int(value))+'.'
            # scale other months
            for k in range(len(all_split_data[j + firstline_iwr]) - 2):
                value = float(all_split_data[j + firstline_iwr][k + 1]) * remaining_demand
                row_data.append(str(int(value))+'.')
        else:
            row_data[2] = str(int(row_data[2])) + '.'
            for k in range(len(all_split_data[j + firstline_iwr]) - 2):
                value = float(all_split_data[j + firstline_iwr][k + 1])
                row_data.append(str(int(value))+'.')
        # append row of adjusted data
        new_data.append(row_data)

    f = open('./scenarios/' + scenario + '/cm2015B_' + scenario + '_' + str(i) + '.iwr', 'w')
    # write firstLine # of rows as in initial file
    for j in range(firstline_iwr):
        f.write(all_data[j])
    for k in range(len(new_data)):
        # write year and ID (spaces after the entry)
        for j in range(2):
            f.write(new_data[k][j] + (lengths[j] - len(new_data[k][j])) * ' ')
        # write all the rest (spaces before the entry)
        for j in range(2, len(new_data[k])):
            f.write((lengths[j] - len(new_data[k][j])) * ' ' + new_data[k][j])
        # write line break
        f.write('\n')
    f.close()
    return None

def writenewDDM(scenario, all_data_DDM, firstline_ddm, CMIP_IWR,
                firstline_iwr, i, users, curtailment_years):
    with open('./scenarios/' + scenario + '/cm2015B_' + scenario + '_' + str(i) + '.iwr') as f:
        sample_IWR = [row for row in f.readlines()[firstline_iwr:]]
    for m in range(len(sample_IWR)):
        sample_IWR[m] = [sample_IWR[m][sum(lengths[:k]):sum(lengths[:k+1])] for k in range(len(lengths))]

    new_data = []
    irrigation_sets = -1

    for j in range(len(all_data_DDM) - firstline_ddm):
        # To store the change between historical and sample irrigation demand (12 months + Total)
        change = np.zeros(13)
        # Split first 3 columns of row on space
        # This is because the first month is lumped together with the year and the ID when splitting on periods
        row = all_data_DDM[j + firstline_ddm]
        row_data = [row[sum(lengths[:k]):sum(lengths[:k+1])] for k in range(len(lengths))]
        # Count number of full sets
        if row_data[1].strip() == '3600507':
            irrigation_sets += 1
        # If the structure is not in the ones we care about then do nothing
        if int(row_data[0]) in curtailment_years and row_data[1].strip() in users:
            index = np.where(irrigation == row_data[1].strip())[0][0]
            line_in_iwr = int(irrigation_sets * len(irrigation) + index)
            for m in range(len(change)):
                change[m] = float(sample_IWR[line_in_iwr][2 + m]) - float(CMIP_IWR[line_in_iwr][2 + m])
                value = float(row_data[m + 2]) + change[m]
                row_data[m + 2] = str(int(value))+'.'
        # append row of adjusted data
        new_data.append(row_data)
        # write new data to file
    f = open('./scenarios/' + scenario + '/cm2015B_' + scenario + '_' + str(i) + '.ddm', 'w')
    # write firstLine # of rows as in initial file
    for j in range(firstline_ddm):
        f.write(all_data_DDM[j])
    for k in range(len(new_data)):
        # write year and ID (spaces after the entry)
        for j in range(2):
            f.write(new_data[k][j] + (lengths[j] - len(new_data[k][j])) * ' ')
        # write all the rest (spaces before the entry)
        for j in range(2, len(new_data[k])):
            f.write((lengths[j] - len(new_data[k][j])) * ' ' + new_data[k][j])
        # write line break
        f.write('\n')
    f.close()
    return None
