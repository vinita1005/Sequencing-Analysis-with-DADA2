import pandas as pd
import csv
import argparse
import numpy as np
import re

parser = argparse.ArgumentParser(description='Remove prefixes in rdp taxonomy')
parser.add_argument('-b', '--blast', nargs='+', help='space seperated parsed blast taxonomy file', required=True)
parser.add_argument('-r', '--rdp', nargs='+', help='space seperated parsed rdp taxonomy file', required=True)
parser.add_argument('-o', '--output', nargs='+', help='output taxonomy file name', required=True)
args = parser.parse_args()

COUNT = 0


def merge_taxonomy(df1, df2):
    print("Starting process")
    global COUNT
    cols = df1.columns.tolist()
    # print(len(df1), len(df2))
    # print(df1.tail(5))
    # print(df2.tail(5))
    with open(args.output[0], 'w', newline='') as csvfile1:
        writer = csv.writer(csvfile1, delimiter='\t')
        writer.writerow([header for header in cols])
        row2 = df2.iloc(1)
        for i, row in df1.iterrows():
            # print("Sequence id1: ", row['#Sequence ID'], "Sequence id2: ", row2[0][i])
            temp_taxa = ""
            if row['taxonomy'] != "" and row['#Sequence ID'] == row2[0][i]:
                taxa = row['taxonomy'].split(";")
                taxa2 = row2[1][i].split(";")
                if len(taxa) < 7 and len(taxa2) > len(taxa):
                    # print("changing taxonomy from: ", taxa, " to: ", taxa2)
                    temp_taxa = row2[1][i]
                    COUNT += 1
                elif "unclassified" in taxa[6] and "unclassified" not in taxa2[6]:
                    # print("changing taxonomy from: ", taxa, " to: ", taxa2)
                    temp_taxa = row2[1][i]
                    COUNT += 1
            elif row['#Sequence ID'] == row2[0][i]:
                # print("changing taxonomy from: ", row['taxonomy'], " to: ", row2[1][i])
                temp_taxa = row2[1][i]
                COUNT += 1
            if temp_taxa != "":
                row['taxonomy'] = temp_taxa
            writer.writerow(row)
    print(COUNT, " taxonomies changed!")
    print("Saving file")


def get_blank_sequence_ids(df1, df2):
    global COUNT
    df1 = df1.merge(df2, how='outer', on='#Sequence ID').fillna('NaN')
    for i, row in df1.iterrows():
        if row['taxonomy_x'] == 'NaN':
            row['taxonomy_x'] = row['taxonomy_y']
            COUNT += 1

    # print(df1)
    df1 = df1.rename(columns={"taxonomy_x": "taxonomy"})
    df1 = df1.drop(columns={"taxonomy_y"})
    # print(df1)
    return df1


if __name__ == '__main__':
    print("Reading files...")
    df1 = pd.read_csv(args.blast[0], delimiter='\t')
    df2 = pd.read_csv(args.rdp[0], delimiter='\t')
    df2.replace(np.nan, '', regex=True, inplace=True)
    df1.replace(np.nan, '', regex=True, inplace=True)
    df1['taxonomy'] = df1['taxonomy'].str.rstrip(";")
    df2['taxonomy'] = df2['taxonomy'].str.rstrip(";")
    df1 = get_blank_sequence_ids(df1, df2)
    print("Sorting blast file.. This might take a while")
    df1 = df1.sort_values(by=['#Sequence ID'])
    # print(df1.head(5))
    print("Sorting rdp file.. This might take a while")
    df2 = df2.sort_values(by=['#Sequence ID'])
    # print(df2.head(5))

    merge_taxonomy(df1, df2)
