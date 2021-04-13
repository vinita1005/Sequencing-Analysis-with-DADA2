import pandas as pd
import csv
import argparse
import re

parser = argparse.ArgumentParser(description='Remove prefixes in rdp taxonomy')
parser.add_argument('-t', '--taxonomy', nargs='+', help='space seperated parsed taxonomy file', required=True)

args = parser.parse_args()
def remove_prefix(df):
    print("Starting process")
    cols = df.columns.tolist()
    with open('transformed_rdp_taxonomy_97.txt', 'w', newline='') as csvfile1:
        writer = csv.writer(csvfile1, delimiter='\t')
        writer.writerow([header for header in cols])
        for index, row in df.iterrows():
            # temp_taxa = row['taxonomy'].replace("k__","").replace("p__","").replace("c__","").replace("o__","").replace("f__","").replace("g__","").replace("s__","")
            # temp_taxa = row['taxonomy'].replace("(*)","")
            temp_taxa = re.sub(r"\(\d+\)", '', row['taxonomy'])
            row['taxonomy'] = temp_taxa
            writer = csv.writer(csvfile1, delimiter='\t')
            writer.writerow(row)

    print("Saving file")
if __name__ == '__main__':
    print(args.taxonomy[0])
    df = pd.read_csv(args.taxonomy[0], delimiter='\t')
    remove_prefix(df)