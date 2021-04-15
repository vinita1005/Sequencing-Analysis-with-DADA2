# Sequencing-Analysis-with-DADA2
16s rRNA data sequencing analysis using DADA2 in QIIME2 and Mothur

This pipeline is created using both QIIME2 and MOTHUR and has many conversions between these two file formats. Please read more about these pipelines in the following tutorials:
QIIME2 : [Moving pictures tutorials](https://docs.qiime2.org/2021.2/tutorials/moving-pictures/)
MOTHUR : [Miseq SOP tutorial](https://mothur.org/wiki/miseq_sop/)

16S rRNA gene sequencing provides extensive and in-depth information about microbial communities and allows differentiation between organisms at the genus level across all major phyla of bacteria. Here, we are going to use the QIIME2 and Mothur pipelines co-operatively on 19 Plates (1651 samples) to resolve ASVs and assign taxonomy to all the unique sequences.

Here are the Sample types in this dataset:
- Positive controls (Pooled)
- Negative controls (Buffer and PCR water)

These sequence files have artifacts and primers already been trimmed off and split into paired forward and reverse reads.

## Pipeline
As explained above, here we are going to do the denoising step in QIIME2(DADA2) and taxonomy assignment in MOTHUR.
<img src="https://user-images.githubusercontent.com/31128057/114905195-ad45be00-9de6-11eb-9b48-112f7b59ea23.png" width="379" height="520">

## 1.	Load Environment
Create and load the environment to work on
```
module load python/anaconda2-4.2.0
conda create -c bioconda -m -p pyenvs/py35-snakemake python=3.5 pandas snakemake
source activate pyenvs/py35-snakemake
module load qiime2
```

## 2. Import Reads
QIIME2 expects all data to be imported in a .qza (QIIME artifact) format. For this command, make sure all your sample reads are kept inside one directory (In this case MIP directory).

```
qiime tools import \
--type 'SampleData[PairedEndSequencesWithQuality]' \
--input-path MIP/*/ \
--input-format CasavaOneEightSingleLanePerSampleDirFmt \
--output-path ./demux-paired-end.qza
```

Once the data is imported as demux-paired-end.qza file, you can convert it to a visualization file in qiime2:
```
qiime demux summarize \
--i-data paired-end-demux.qza \
--o-visualization demux.qzv
```
View this file by uploading it to https://view.qiime2.org/

You can find useful information here like this:
![image](https://user-images.githubusercontent.com/31128057/114616022-5f10ad80-9c74-11eb-96ed-4bd6c6f49c42.png)

This is what the interactive quality plot for forward and reverse reads looks like:
![image](https://user-images.githubusercontent.com/31128057/114616301-ac8d1a80-9c74-11eb-9568-ffcac4f0c672.png)
You can zoom the plots by dragging the cursor on the graphs. Use this graph to decide on the value for the truncation length parameter for next step.
General rule I apply is to truncate to the point where quality score goes below 25 or 20.

## 3. Denoising with DADA2
Here, instead of going through quality filter -> denoise -> chimera removal steps, we are going to apply the DADA2 pipeline available in QIIME2.

For this to work efficiently, its important that you truncate as much of the lower quality portions of reads as possible, but leave enough overlap that the forward and reverse can be merged without any problems.
I have chosen p-trunc-len-f=260 and p-trunc-len-r=240 for this data.

```
qiime dada2 denoise-paired \
--i-demultiplexed-seqs demux.qza \
--p-trim-left-f 9 \
--p-trim-left-r 9 \
--p-max-ee-f 5 \
--p-max-ee-r 5 \
--p-trunc-len-f 260 \
--p-trunc-len-r 240 \
--p-n-threads 32 \
--p-n-reads-learn 100000 \
--o-table table.qza \
--o-representative-sequences rep-seqs.qza \
--o-denoising-stats denoising-stats.qza \
--verbose
```
You can find the detailed explanation of each of these commands at: https://docs.qiime2.org/2021.2/plugins/available/dada2/denoise-paired/?highlight=denoise%20paired

Output of the DADA2 command will include - ASV table, representative sequences and some statistics. You can convert these file into qiime2 visualization artifacts and view them in https://view.qiime2.org/
Here, you will see the detailed information from each of the steps of dada2. After the end step of chimera removal, we have 75-80% reads retained for most of the samples. If you observe the amount of reads to be drastically reduced, you can try to change the truncate parameter an try again. Make sure you leave good amount of overlap betwen forward and reverse reads (atleast 12).
![image](https://user-images.githubusercontent.com/31128057/114618556-7b621980-9c77-11eb-9f0e-c4bb20bec687.png)

After the denoising step, you can assign taxonomy using the ASV table and representative sequences. This step is done in the MOTHUR pipeline instead of QIIME2.
To make the qiime2 artifact compatible in mothur, we have to import it in a format that mothur will accept. To do that, you can export your table.qza files to biom using the QIIME2 command export and then convert this biom file to txt to work with in mothur. As for the rep-seqs.qza, QIIME2 will convert it to .fasta file.

### Convert rep-seqs.qza and table.qza into biom
```
qiime tools export \
--input-path rep-seqs.qza \
--output-path rep-seqs

qiime tools export \
--input-path table.qza \
--output-path table
```

QIIME2 will give you feature-table.biom as an output from exporting table.qza. Now, to convert this to a count_table which is required in mothur, follow these steps:

So first, we need to initialize our MOTHUR environment.

```
module use /*/projectmodules
module load mothur/1.44.3
```
```
1. biom convert -i feature-table.biom -o feature-table.txt --to-tsv   > This step will convert your biom file to tab separated txt file.
2. biom convert -i feature-table.txt -o feature-table.biom --table-type="OTU table" --to-json   > This will again convert your txt file to biom in json format. This step is to avoid the noise which might be induced in the next step. Since the biom file from QIIME2 is in hdf5 format instead of json, this might give you trouble and you might find some missing values in the count table later on.
3. biom.info(biom=feature-table.biom)  > Convert your biom file to a shared file in mothur
4. count.seqs(shared=feature-table.userLabel.shared, compress=f)  > convert the shared file to count_table
```
Now you are ready to process your files in MOTHUR.

## 4. Assigning Taxonomy
Here, Mothur has a classify.seqs command to assign taxonomy. But before that, you need to decide which reference database you are going to use. I have used the HOMD database here as a reference. Make sure you have the latest version of the database. You will need two files - HOMD_16S_rRNA_RefSeq_Vxx.xx.fasta file which contains the reference reads and HOMD_16S_rRNA_RefSeq_V15.22.mothur.taxonomy file which contains the taxonomy.

Next step is to decide on a cuoff value for the taxonomy assignment. Cutoff value defines the confidence of the algorithm on the taxonomy assignment. A match is rejected if the confidence value is lower than the cutoff. There are many methods by which you can assign the taxonomy, we are going to explore two of them here - blast consensus and RDP (sklearns in QIIME2).

### a. Blast
The blast taxonomy assignment here is done using a script which runs on qiime1. You can find the script in the repository code : Blast_99.sh.
```
blastn -query dna-sequences.fasta -task megablast -db HOMD  -perc_identity 97 -qcov_hsp_perc 97 -max_target_seqs 5000 -outfmt "7 qacc sacc qstart qend sstart send length pident qcovhsp qcovs" -out blast_taxonomy
```
The output produced by this has a different format than a normal taxonomy file. Hence, to convert this in mothur friendly format, use following steps:
```
Use the blast_parse.py python script for conversion.
### usage ###
python blast_parse.py -i blast_taxonomy -o parsed_blast_taxonomy
```
This will provide a result which you can view in excel:
![image](https://user-images.githubusercontent.com/31128057/114626254-6d18fb00-9c81-11eb-81e6-046bb175fec0.png)

As you can see, instead of the taxonomy, this file provides a Identity field with the id associated with the taxonomy in the reference database. To replace this field with the actual taxonomy value, use the following script:
```
Use make_taxonomy_table.py
### usage ###
python make_taxonomy_table.py -b blast_taxonomy -t HOMD_16S_rRNA_RefSeq_Vxx.xx.mothur.taxonomy -u final_blast_taxonomy
```

### b. RDP
RDP however is executed on MOTHUR since I found that sklearns in qiime2 has only 30-40% of hits in total.
```
classify.seqs(fasta=../dna-sequences.good.filter.fasta, count=../feature-table.userLabel.userLabel.count_table, reference=../reference_dbs/HOMD_16S_rRNA_RefSeq_V15.22.fasta, taxonomy=../reference_dbs/HOMD_16S_rRNA_RefSeq_V15.22.mothur.taxonomy, cutoff=97)
```
Sometimes, the RDP taxonomy has some prefixs (k__, s__, etc) to identify levels of taxonomy or some suffixes ([100],[99],etc) to indicate the confidence value. These must be removed to maintain a proper format for the taxonomy file. This is done using the remove_rdp_prefix.py python script.
```
### usage ###
python remove_rdp_prefix.py -t rdp_taxonomy.txt
```

In the end, I combined the two taxonomy files that I got such that, the sequences which are unassigned at the species level in blast taxonomy, will be replaced by the taxonomy found in RDP. The python script merge_blast_rdp.py does this step.
```
### merge_blast_rdp.py usage ###
python merge_blast_rdp.py -b final_blast_taxonomy -r rdp_taxonomy -o merged_taxonomy.txt
```

## 5. Get the final count_table with the taxonomy
Lastly, we want to get the final count table with the taxonomy for each unique sequence.
```
Use merge_taxonomy_table.py python script
### usage ###
python merge_taxonomy_table.py -t merged_taxonomy.txt -o final_feature_table.txt
```

## References

[1] A full example workflow for amplicon data, https://astrobiomike.github.io/amplicon/dada2_workflow_ex

[2] Amplicon Sequencing Data Analysis with Qiime 2, https://github.com/Gibbons-Lab/isb_course_2020/blob/master/16S_solutions.ipynb

[3] Current challenges and best-practice protocols for microbiome analysis, https://academic.oup.com/bib/article/22/1/178/5678919

[4]. A practical guide to amplicon and metagenomic analysis of microbiome data, https://link.springer.com/article/10.1007/s13238-020-00724-8

[5] Comparing bioinformatic pipelines for microbial 16S rRNA amplicon sequencing, https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0227434
