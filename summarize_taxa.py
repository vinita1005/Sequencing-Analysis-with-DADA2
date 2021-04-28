import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Remove prefixes in rdp taxonomy')
parser.add_argument('-t', '--taxonomy', nargs='+', help='space seperated count table file with taxonomy', required=True)

args = parser.parse_args()


def get_seq_count(df, classes):
    result_seqs = {}
    result_reads = {}

    for i,taxa_class in enumerate(classes):
        if i+1 != len(classes):
            df_filtered = df[~df[taxa_class].str.contains('~*unclassified', regex= True, na=False)
                             & df[classes[i+1]].str.contains('~*unclassified', regex= True, na=False)]
        else:
            df_filtered = df[~df[taxa_class].str.contains('~*unclassified', regex=True, na=False)]
        result_seqs[taxa_class] = df_filtered[taxa_class].count()
        result_reads[taxa_class] = df_filtered['total'].sum()
    print("# Unique sequences: ", result_seqs)
    print("# Reads: ", result_reads)


if __name__ == '__main__':

    print("Reading file...")
    df = pd.read_csv(args.taxonomy[0], delimiter='\t')
    df_filtered = df[["#OTU ID", "total", "taxonomy"]]
    df_filtered['taxonomy'] = df_filtered['taxonomy'].str.rstrip(";")
    classes = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
    df_filtered[['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']] = \
        df_filtered.taxonomy.str.split(";", expand=True, )

    print("Getting count...")
    get_seq_count(df_filtered, classes)
