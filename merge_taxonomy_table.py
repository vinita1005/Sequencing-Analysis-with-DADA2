import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Merge all tables into OTU table')
parser.add_argument('-t', '--tax_res', nargs='+', help='space seperated tables', required=True)
parser.add_argument('-o', '--output_fp', help='uncollapsed OTU table file path', required=True)

args = parser.parse_args()

if __name__ == "__main__":
    dfs = []
    for res in args.tax_res:
        res_df = pd.read_csv(res, sep='\t', index_col=0)
        dfs.append(res_df)
    df = dfs[0]
    for x in dfs[1:]:
        df = df.join(x, how='outer').fillna('NaN')
    df.to_csv(args.output_fp, sep='\t', index=True, index_label='#OTU ID')

