import pandas as pd
import argparse
import os.path

parser = argparse.ArgumentParser(description='Parse a BLAST result to a single columns dataframe.')
parser.add_argument('-i', '--input_fp', help='blast result file', required=True)
parser.add_argument('-o', '--output_fp', help='output file', required=True)
args = parser.parse_args()


if __name__ == '__main__':
    res_dict = {}
    marker = 0
    with open(args.input_fp) as f:
        for line in f:
            if line.startswith('# BLAST'):
                marker = 0
            else:
                marker += 1

            if marker == 5:
                content = line.strip().split('\t')
                query_id = content[0]
                target_id = content[1]
                identity = float(content[7])
                coverage = float(content[8])

                res_dict[query_id] = [target_id,str(identity),str(coverage)]

    columns = [os.path.splitext(os.path.basename(args.input_fp))[0]]
    # res_df = pd.DataFrame.from_dict(res_dict, orient='index', columns=['Target','Identify','Coverage']).rename_axis('#Sequence ID').reset_index()
    res_df = pd.DataFrame.from_dict(res_dict, orient='index')
    res_df.columns = ['Target','Identify','Coverage']
    res_df.to_csv(args.output_fp, sep='\t')