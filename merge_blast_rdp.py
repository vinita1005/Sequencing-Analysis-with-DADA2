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

def merge_taxonomy(df1, df2):
    print("Starting process")
    cols = df1.columns.tolist()
    count = 0
    with open(args.output[0], 'w', newline='') as csvfile1:
        writer = csv.writer(csvfile1, delimiter='\t')
        writer.writerow([header for header in cols])
        row2 = df2.iloc(1)
        for i, row in df1.iterrows():
            if row['taxonomy'] != "":
                taxa = row['taxonomy'].split(";")
                taxa2 = row2[1][i].split(";")
                if len(taxa) < 7 and len(taxa2) > len(taxa):
                    print("changing taxonomy from: ", taxa, " to: ", taxa2)
                    row['taxonomy'] = row2[1][i]
                    count += 1
                elif "unclassified" in taxa[6] and "unclassified" not in taxa2[6]:
                    print("changing taxonomy from: ", taxa, " to: ", taxa2)
                    row['taxonomy'] = row2[1][i]
                    count += 1
            else:
                print("changing taxonomy from: ", row['taxonomy'], " to: ", row2[1][i])
                row['taxonomy'] = row2[1][i]
                count += 1
            writer.writerow(row)
    print(count, " taxonomies changed!")
    print("Saving file")


if __name__ == '__main__':
    print("Reading files...")
    df1 = pd.read_csv(args.blast[0], delimiter='\t')
    df2 = pd.read_csv(args.rdp[0], delimiter='\t')
    df2.replace(np.nan, '', regex=True, inplace=True)
    df1.replace(np.nan, '', regex=True, inplace=True)
    df1['taxonomy'] = df1['taxonomy'].str.rstrip(";")
    df2['taxonomy'] = df2['taxonomy'].str.rstrip(";")
    print("Sorting blast file.. This might take a while")
    df1.sort_values(by=['#Sequence ID'])
    print("Sorting rdp file.. This might take a while")
    df2.sort_values(by=['#Sequence ID'])
    merge_taxonomy(df1, df2)
