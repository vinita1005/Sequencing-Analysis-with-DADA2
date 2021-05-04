#!/bin/sh

#SBATCH --partition=general-compute
#SBATCH --time=71:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --job-name="16s_Analysis"
#SBATCH --output=16s_Analysis.log

while getopts d: flag
do
	case "${flag}" in 
		d) dada2_direc=${OPTARG};;
	esac
done

if [ -z "$dada2_direc" ];
then
	echo 'No directory path provided for dada2 output files. Please see the usage: '
	echo 'Usage: ./16s_analysis_pipeline -d <directory_path>'
	exit
fi

echo 'directory: ' $dada2_direc

REF_DB_DIREC="/projects/academic/pidiazmo/vinita/ref_db"

START=`date +%s`

echo 'STEP 1: Loading environment...'
module load qiime2
conda activate /projects/academic/pidiazmo/projectsoftwares/env/qiime2-2020.8

if [ $? -eq 0 ];
then
	echo 'STEP 2: Exporting DADA2 output'
	qiime tools export \
	--input-path ./$dada2_direc/rep-seqs.qza \
	--output-path ./rep-seqs
	
	qiime tools export \
	--input-path ./$dada2_direc/table.qza \
	--output-path ./table
else
	exit
fi

if [ $? -eq 0 ];
then
	echo 'STEP 3: Loading Mothur environment...'
	module use /projects/academic/pidiazmo/projectmodules
	module load mothur/1.44.3
fi

echo 'STEP 4: Generating count table...'
if [ $? -eq 0 ];
then
	biom convert -i ./table/feature-table.biom -o ./table/feature-table.txt --to-tsv	
	biom convert -i ./table/feature-table.txt -o ./table/feature-table.biom
	mothur "#biom.info(biom=./table/feature-table.biom, format=hdf5)"
	mothur "#count.seqs(shared=./table/feature-table.userLabel.shared, compress=f)"
fi

if [ $? == 0 ];
then
	echo 'STEP 5: Creating link for feature-table and rep-sequences...'
	ln -s ./table/feature-table.userLabel.userLabel.count_table ./feature-table.userLabel.userLabel.count_table
	ln -s ./rep-seqs/dna-sequences.fasta ./dna-sequences.fasta
fi

echo 'STEP 6: Assigning blast taxonomy...'
./Blast_99.sh


echo 'STEP 7: Converting blast taxonomy file...'
python blast_parse.py -i ./blast_99_taxonomy -o ./parsed_blast_taxonomy

echo 'STEP 8: Mapping taxonomy name to identity colum in blast taxonomy file...'
python make_taxonomy_table.py -b ./parsed_blast_taxonomy -t $REF_DB_DIREC/HOMD_16S_rRNA_RefSeq_V15.22.mothur.taxonomy -u ./final_blast_taxonomy

echo 'STEP 9: Assiging rdp taxonomy...'
mothur "#classify.seqs(fasta=./dna-sequences.fasta, count=./feature-table.userLabel.userLabel.count_table, reference="$REF_DB_DIREC"/HOMD_16S_rRNA_RefSeq_V15.22.fasta, taxonomy="$REF_DB_DIREC"/HOMD_16S_rRNA_RefSeq_V15.22.mothur.taxonomy)"

echo 'STEP 10: Removing rdp prefix and suffixes...'
python remove_rdp_prefix.py -t dna-sequences.mothur.wang.taxonomy

echo 'STEP 11: Merging blast and rdp results'
python merge_blast_rdp.py -b final_blast_taxonomy -r transformed_rdp_taxonomy.txt -o merged_taxonomy.txt

echo 'STEP 12: Getting final feature table with taxonomy...'
python merge_taxonomy_table.py -t feature-table.userLabel.userLabel.count_table merged_taxonomy.txt -o final_feature_table.txt

echo 'Feature table creation complete...'
echo 'Saved file to: final_feature_table.txt'
END=`date +%s`
ELAPSED=$(( $END - $START ))

echo 'It took: '$ELAPSED' s'