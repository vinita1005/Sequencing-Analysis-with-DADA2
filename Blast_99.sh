#!/bin/sh
#SBATCH --partition=general-compute
#SBATCH --time=8:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --job-name="blast99"
#SBATCH --output=blast99.log

set -e

module load python/anaconda
module load R/3.1.2
module load qiime/1.9.1


echo '--------------------'
echo 'preprocessing...'
START=`date +%s`


/projects/academic/pidiazmo/Pipeline/blast+/2.6.0/bin/makeblastdb -in /projects/academic/pidiazmo/vinita/ref_db/HOMD_16S_rRNA_RefSeq_V15.22.fasta -out HOMD -dbtype 'nucl' -input_type fasta

/projects/academic/pidiazmo/Pipeline/blast+/2.6.0/bin/blastn -query ./dna-sequences.fasta -task megablast -db HOMD  -perc_identity 99 -qcov_hsp_perc 99 -max_target_seqs 5000 -outfmt "7 qacc sacc qstart qend sstart send length pident qcovhsp qcovs" -out blast_99_taxonomy


END=`date +%s`
ELAPSED=$(( $END - $START ))
echo "preprocessing takes "$ELAPSED " s"