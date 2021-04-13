import pandas as pd
import csv
import argparse
import numpy as np


parser = argparse.ArgumentParser(description='Remove prefixes in rdp taxonomy')
parser.add_argument('-b', '--blast', nargs='+', help='space seperated parsed blast taxonomy file', required=True)
parser.add_argument('-r', '--rdp', nargs='+', help='space seperated parsed rdp taxonomy file', required=True)

args = parser.parse_args()

def merge_taxonomy(df1, df2):
    print("Starting process")
    cols = df1.columns.tolist()
    count = 0
    with open('merged_taxonomy_99.txt', 'w', newline='') as csvfile1:
        writer = csv.writer(csvfile1, delimiter='\t')
        writer.writerow([header for header in cols])
        row2 = df2.iloc(1)
        for i, row in df1.iterrows():
            if i != 0:
                # print("new iteration")
                if row['taxonomy'] != "":
                    # print("row[taxonomy] : ",row['taxonomy'])
                    taxa = row['taxonomy'].split(";")
                    print("row: ", taxa)
                    taxa2 = row2[1][i].split(";")
                    # print(len(taxa2),",",len(taxa))
                    print("row2: ",taxa2)
                    if len(taxa) < 7 and len(taxa2) > len(taxa):
                        print("changing taxonomy")
                        row['taxonomy'] = row2[1][i]
                        count += 1
                else:
                    row['taxonomy'] = row2[1][i]
                    count += 1
                writer.writerow(row)
    print(count," taxonomies changed!")
    print("Saving file")

if __name__ == '__main__':
    # print(args.blast[0])
    df1 = pd.read_csv(args.blast[0], delimiter='\t')
    df2 = pd.read_csv(args.rdp[0], delimiter='\t')
    df2.replace(np.nan, '', regex=True, inplace=True)
    df1.replace(np.nan, '', regex=True, inplace=True)
    merge_taxonomy(df1, df2)