import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Merge all parsed BLAST results into OTU table')
parser.add_argument('-b', '--blast_res', nargs='+', help='space seperated parsed BLAST result', required=True)
parser.add_argument('-t', '--taxonomy_fp', help='taxonomy file for OTU annotation', required=True)
parser.add_argument('-u', '--uncollapsed_fp', help='uncollapsed OTU table file path', required=True)

args = parser.parse_args()

def get_id_2_lable(tax_file):
    id_2_label = {}
    with open(tax_file) as f:
        for line in f:
            content = line.strip().split('\t')
            taxa_id = content[0]
            taxa_label = content[1]
            id_2_label[taxa_id] = taxa_label
    return id_2_label

if __name__ == "__main__":
    dfs = []
    for res in args.blast_res:
        res_df = pd.read_csv(res, sep='\t', index_col=0)
        # res_df.index = res_df.index.astype('str')
        dfs.append(res_df)
    df = dfs[0]
    for x in dfs[1:]:
        df = df.join(x, how='outer').fillna(0)

    sample_ids = list(df.columns)
    id_2_label = get_id_2_lable(args.taxonomy_fp)
    df.loc[:, 'taxonomy'] = df.loc[:,'Target'].map(lambda x: id_2_label[str(x)])
    df.to_csv(args.uncollapsed_fp, sep='\t', index=True, index_label='#Sequence ID')

