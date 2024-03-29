#RAW DATA QC#
pf status --type study  --id 5582
pf info --type sample --id 5582STDY7724227
pf data -t study --id 5582
pf data -t lane --id 28204 --symlink --filetype bam #command for picking mapped data and saving it to my folder/data for lane 28203
pf data -t lane --id 28204 --symlink --filetype bam # this command and the upper one picked mapped data, but idea is to re-map it yourself.

#MAPPING DATA TO REF #already mapped to reference version 7, checked command for mapping data to, with James
pf map -t lane --id 28203  ## command to check the mapped bam files for the lane 28203
pf info -t lane --id 28203  # 108 samples # shows samples mapped on that lane
pf info -t lane --id 28204  # 66 samples : shows samples mapped on that lane
pf map - t lane --id 28203 - s 28203 _stats.csv
pf status - t lane --id 28204

#ames help with crosschecking the new ref with some contigs removed compared to the old ref.#21/02/2019
grep '^>' Schistosoma_mansoni_v7.fa  #look at current ref v7
pf ref -t species --id Schistosoma #look at schisto references in the db
pf status -t study --id 5582  #main command to check mapping progress for the whole study

#picking fastq files#
pf data -t lane --id 28203 --symlink --filetype fastq
pf data -t lane --id 28204 --symlink --filetype fastq

#Variant Calling 4th March 2019#install gatk using command below;

wget https://github.com/broadinstitute/gatk/releases/download/4.1.0.0/gatk-4.1.0.0.zip
unzip filename  # used unzip command to unzip the file downloaded
# cd to folder of the unzipped file and check if the gatk file exits

/lustre/scratch118/infgen/team133/jt24/Software/gatk-4.1.0.0$  #path for gatk

gatk-4.1.0.0/gatk --java-options "-Xmx13G" HaplotypeCaller -R  Ref/Schistosoma_mansoni_v7.fa - I /pathfind_28204 /100718.pe.markdup.bam -O 100718.vcf

# at first code did  ot work, and this was because gatk required java version 1.8 not 1.7 which was set as default on the Sanger farm.
# edited this to make the code work somehow though not fully,
# though it also required first indexing the reference genome v7

samtools faidx Schistosoma_mansoni_v7.fa ### used this command to index the reference

# genome i.e the bsup command did not work.
# run this on the refernce to create .fa.fai file

gatk-4.1.0.0/gatk --java-options "-Xmx13G" HaplotypeCaller -R  Ref/Schistosoma_mansoni_v7.fa -I pathfind_28204/100718.pe.markdup.bam -O 100718.vcf

#after indexing the ref, the command gave an error requiring creating a sequence dictionary #seq dict helps to variant call easily
#creating sequence dictionary

gatk-4.1.0.0/gatk CreateSequenceDictionary -R Ref/Schistosoma_mansoni_v7.fa #command for creating the seq dict using gatk

#after that i submit the job with the variant calling command, see full command below;

bsub.py --threads 2 -q long 13 100718_variants gatk-4.1.0.0/gatk --java-options "-Xmx13G" HaplotypeCaller -R  \
    Ref/Schistosoma_mansoni_v7.fa -I pathfind_28204/100718.pe.markdup.bam -ERC GVCF -O 100718.gvcf

# 7th March 2019 submitting jobs for all other samples # to keep editing the command to suit the sample IDs

#8th March 2019#
#submitting jobs all at once using one command, first create a list of the
parallel --dry-run "bsub.py --threads 2 -q basement 13 {}_variants gatk-4.1.0.0/gatk --java-options \"-Xmx13G \ " \
                   "\" HaplotypeCaller -R  Ref/Schistosoma_mansoni_v7.fa -I pathfind_28203/{}.pe.markdup.bam -ERC GVCF -O {}.gvcf" :::: pathfind_28203.list

#outputting the file into an .sh and using chmod to excute it
parallel --dry-run "bsub.py --threads 2 -q basement 13 {}_variants gatk-4.1.0.0/gatk --java-options \"-Xmx13G" \
                   "\" HaplotypeCaller -R  Ref/Schistosoma_mansoni_v7.fa -I pathfind_28203/{}.pe.markdup.bam -ERC GVCF -O {}.gvcf" :::: unsub28204.txt > submit_28204.sh

#some commands#
parallel --dry-run "bsub.py --threads 2 -q long 13 {}_variants gatk-4.1.0.0/gatk --java-options \"" \
                   "-Xmx13G\" HaplotypeCaller -R  Ref/Schistosoma_mansoni_v7.fa -I pathfind_28203/{}.pe.markdup.bam -ERC GVCF -O {}.gvcf":::: unsub28204.txt > submit_28204.sh

comm -23  <(sort 28204_all) <(sort submitted28204.txt) > unsub28204.txt # command used to sort the files and remove those i had already submitted their jobs,
# sort first file then sort second file = this removed the duplicated in this case ,
#separting the already submitted from the un-submitted and outputting a new files as un-submitted.

nano submitted28204.txt # making a file name for the submitted data
ls pathfind_28204 | cut -d"." -f1 | sort | uniq > 28204_all  #checking files
ls pathfind_28204 | cut -d"." -f1 | sort | uniq | wc -l
cut -d"." -f1 pathfind_28204  ## selecting samples in the file separated by.

101460/100802_varia

bjobs -w | grep basement | grep PEND  | awk '{s="bswitch long "$1; system(s)}'
bjobs -w | grep basement | grep RUN

#12th march 2019#
/lustre/scratch118/infgen/pathogen/pathpipe/helminths/seq-pipelines/Schistosoma/mansoni/TRACKING/5582/5582STDY7759895/ # file path for the samples

pf data -t sample --id 5582STDY7759895 --symlink --filetype bam
pf info -t lane --id 28204

#putting some samples on farm 15/03/2019
bsub.py --threads 2 -q basement 13 103370_variants gatk-4.1.0.0/gatk \
        --java-options "-Xmx13G" HaplotypeCaller -R  Ref/Schistosoma_mansoni_v7.fa -I pathfind_5582STDY7759895/103370.pe.markdup.bam -ERC GVCF -O 103370.gvcf

pf data -t sample --id 5582STDY7759895 --symlink --filetype bam

#Variant QC combining gvcf into one#
bsub.py --threads 3 -q basement 17 combinedgvcfs gatk-4.1.0.0/gatk --java-options "-Xmx17G" CombineGVCFs \
                                                        --reference Schistosoma_mansoni_v7.fa --arguments_file GVCFs.txt -O combined.g.vcf

bsub.py --threads 4 -q basement 10 combine_201 gatk --java-options "-Xmx10G" CombineGVCFs -R ../Ref_nohap/Sm_v7_nohap.fa -V 174_new.g.vcf -V ../test.g.vcf -O 201_new.g.vcf

gatk CombineVariants --arguments_file arg.list -o cohort.chr1.g.vcf -L chr1
gatk CombineVariants --arguments_file arg.list -o cohort.chr2.g.vcf -L chr2
gatk CombineVariants --arguments_file arg.list -o cohort.chr3.g.vcf -L chr3

#arg.list:
-V sample1.g.vcf
-V sample2.g.vcf

# my151gvcf = name of database containing combined gvcfs
#29/03/2019
# made a list and add the --variant to be able to use it in th command for Combinegvcfs

ls *.g.vcf > myList.txt
cat myList.txt | sed 's/^/--variant /g' > myNew.txt

#means at the start of the line
#combining gvcfs

head -3000 174_new.g.vcf | grep "CHROM" | tr '\t' '\n' | grep "STDY" -c  #counting how many samples are being combined
head -3000 174_new.g.vcf | grep "CHROM" | tr '\t' '\n' | grep "STD" | grep "5582STDY7759906"
head -3000 combined.g.vcf | grep "CHROM" | tr '\t' '\n' | grep "STD"
head -3000 combined.g.vcf | grep "CHROM" | tr '\t' '\n' | grep "STD" | less
head -3000 combined.g.vcf | grep "CHROM" | less

# Joint call cohort/
bsub.py --threads 3 -q basement 10 genotype_174_new gatk --java-options "-Xmx10G" GenotypeGVCFs -R ../Ref_nohap/Sm_v7_nohap.fa -V 174_new.g.vcf -O 174_new.vcf
bsub.py --threads 3 -q basement 10 genotype201_new gatk --java-options "-Xmx10G" GenotypeGVCFs -R ../Ref_nohap/Sm_v7_nohap.fa -V 201_new.g.vcf -O 201_new.vcf

#Combining my gvcf with that of outgroup
#Collable_loci
#for checking percentage of reads mapping to the correctly to the genome

bsub.py --threads 4 -q normal 2 101649_collable.bam gatk-4.1.0.0/gatk -T CallableLoci -R Ref/Schistosoma_mansoni_v7.fa -I Mapped_2/101649.pe.markdup.bam -summary 101649_table.txt -o 101649_callable_status.bed

#*** Variants to table
bsub.py --threads 2 -q normal 2 NovaSeq174_v2table gatk-4.1.0.0/gatk --java-options "-Xmx2G"  VariantsToTable -V NovaSeq_174.vcf -F CHROM -F POS -F MQ -F QD -F FS -F SOR -F MQRankSum -F ReadPosRankSum -O results.table
bsub.py --threads 3 -q long 4 VJ_174_res.table gatk-4.1.0.0/gatk --java-options "-Xmx4G" VariantsToTable -V combined_VIANNEY_174.vcf -F CHROM -F POS -F MQ -F QD -F FS -F SOR -F MQRankSum -F ReadPosRankSum -O Vianney_174_results.table
bsub.py --threads 3 -q long 4 JVT_174_SNPs gatk-4.1.0.0/gatk --java-options "-Xmx4G" VariantsToTable -V Nohap_174_SNPs.vcf -F CHROM -F POS -F MQ -F QD -F FS -F SOR -F MQRankSum -F ReadPosRankSum -O SNPs_174_res.table
bsub.py --threads 3 -q long 4 201_SNPs gatk-4.1.0.0/gatk --java-options "-Xmx4G" VariantsToTable -V Nohap_201_SNPs.vcf -F CHROM -F POS -F MQ -F QD -F FS -F SOR -F MQRankSum -F ReadPosRankSum -O SNPs_201_res.table

#selecting SNPs and indels
bsub.py --threads 3 -q basement 10 select.SNPs \
    gatk --java-options "-Xmx10G" SelectVariants -R Ref_nohap/Sm_v7_nohap.fa -V 174_new.vcf --select-type-to-include SNP -O 174_SNPs_new.vcf

bsub.py --threads 3 -q long 10 Nohap_SNPs_174 gatk-4.1.0.0/gatk --java-options "-Xmx10G" SelectVariants -R Ref_nohap/Sm_v7_nohap.fa -V combined_VIANNEY_174.vcf --select-type-to-include SNP -O Nohap_174_SNPs.vcf

bsub.py --threads 3 -q basement 10 select_201 \
    gatk --java-options "-Xmx10G" SelectVariants -R Ref_nohap/Sm_v7_nohap.fa -V 201_new.vcf --select-type-to-include SNP -O 201_SNPs_new.vcf

bsub.py --threads 3 -q normal 10 NovaSeq174_Indels gatk-4.1.0.0/gatk --java-options "-Xmx10G" SelectVariants -R Schistosoma_mansoni_v7.fa -V NovaSeq_174.vcf --select-type-to-include INDEL -O 174_Indels.vcf
bsub.py --threads 3 -q normal 10 Exclude_SNPs gatk-4.1.0.0/gatk --java-options "-Xmx10G" SelectVariants -R Schistosoma_mansoni_v7.fa -V NovaSeq_174.vcf --select-type-to-exclude SNP -O Excluded_SNPs.vcf

# Variant filtering 10/04/2019 # write command to bash file to run
bsub.py --threads 3 -q normal 10 Filtered_SNPs gatk-4.1.0.0/gatk --java-options "-Xmx10G" VariantFiltration -R Schistosoma_mansoni_v7.fa -O Filtered_SNPs.vcf \
        -V 174_SNPs.vcf --filterExpression 'QD < 2.0 || MQ < 40.0 || FS > 60.0 || SOR > 3.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0' --filterName "Filters_SNPs"

bsub.py --threads 3 -q long 4 Filter_201 \
      gatk-4.1.0.0/gatk --java-options "-Xmx4G" VariantFiltration -R Ref_nohap/Sm_v7_nohap.fa -O Filtered_SNPs_201.vcf \
    -V Nohap_201_SNPs.vcf --filter-expression 'QD < 2.0 || MQ < 40.0 || FS > 60.0 || SOR > 3.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0' --filter-name "Filters_SNPs"

bsub.py --threads 3 -q long 4 Filter.174.new \
  gatk --java-options "-Xmx4G" VariantFiltration -R Ref_nohap/Sm_v7_nohap.fa -O 174_HardFiltered.SNPs_new.vcf \
  -V 174_SNPs_new.vcf --filterExpression "QD < 2.0 || MQ < 40.0 || FS > 60.0 || SOR > 3.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0" \
                                         --filterName "Filters_SNPs"

bsub.py --threads 3 -q normal 10 Filtered_Indqels gatk-4.1.0.0/gatk --java-options "-Xmx10G" VariantFiltration -R Schistosoma_mansoni_v7.fa -O Filtered_Indels.vcf \
        -V Excluded_SNPs.vcf --filterExpression "QD < 2 || ReadPosRankSum < -20.0 || InbreedingCoeff < -0.8 || FS > 200.0 || SOR > 10.0" --filterName "Filters_Indels"

gatk-4.1.0.0/gatk --java-options "-Xmx10G" VariantFiltration -R Schistosoma_mansoni_v7.fa -O Excluded_SNPs.vcf --V Filtered_ExcludedSNPs.vcf \
 --filter-expression 'QD < 2.0 || ReadPosRankSum < -20.0 || FS > 200.0 || SOR > 10.0 || InbreedingCoeff < -0.8' --filter-name "Filters_Indels"

#the filtering commands were written in bash files "Filtered_SNPs" and 'Excluded_SNPs" in the directory Variants
#merge VCFs
bsub.py --threads 3 -q normal 10 Merged_vcf gatk-4.1.0.0/gatk --java-options "-Xmx10G" MergeVcfs -I Filtered_SNPs.vcf -I Filtered_ExcludedSNPs.vcf -O Filtered_Merged.vcf

gatk-4.1.0.0/gatk --java-options "-Xmx10G" MergeVcfs -I ExcludedFiltered_Merged.vcf -I Clean_Outgroup.vcf -O Clean_Myvcf_Outgroup.vcf

#Counting NUMBER OF SNPs/8th april 2020
bsub.py --threads 2 -q normal 2 NovaSeq174_v2table gatk-4.1.0.0/gatk --java-options "-Xmx2G"  VariantsToTable -V 174_SNPs.vcf -F CHROM -F POS -O 174_SNPs.table #not good, use bcftools stats
bsub.py --threads 3 -q normal 10 NofrawSNPs gatk-4.1.0.0/gatk --java-options "-Xmx10G" bcftools-1.5 stats Excluded_SNPs.vcf -O rawExcludedSNPs.vcf

bcftools-1.5 stats Excluded_SNPs.vcf > rawExcludedSNPs.vcf
bcftools-1.5 stats 174_SNPs.vcf > rawSNPs.vcf
bcftools-1.5 stats NovaSeq_174.vcf > mixed.vcf
bcftools-1.5 stats Filtered_Merged.vcf > filtered_variants.vcf
bcftools-1.5 stats Filtered_SNPs.vcf > filteredsnps.vcf
bcftools-1.5 stats Filtered_ExcludedSNPs.vcf > filteredexcludedsnps.vcf
bcftools-1.5 stats ExcludedFiltered_Merged.vcf > filteredexcludedmerged_all.vcf

#to select variants using gatk and remove snps and indels that did not pass the filters

bsub.py --threads 3 -q long 10 Exclude.filtered174 \
    gatk --java-options "-Xmx10G" SelectVariants -R Ref_nohap/Sm_v7_nohap.fa -V 174_HardFiltered.SNPs_new.vcf  --exclude-filtered -O 174.only.Hfiltered.SNPs_new.vcf

bsub.py --threads 3 -q normal 10 ExcludedSNPs_Indels gatk-4.1.0.0/gatk --java-options " -Xmx10G" SelectVariants -R Schistosoma_mansoni_v7.fa -V Filtered_ExcludedSNPs.vcf  --exclude-filtered -O ExcludedFilteredSNPs_Indels.vcf

bsub.py --threads 3 -q long 4 Passedf_174 gatk-4.1.0.0/gatk --java-options "-Xmx4G" SelectVariants -R Ref_nohap/Sm_v7_nohap.fa -V Filtered_SNPs_174.vcf --exclude-filtered -O Passedf_SNPs_174.vcf

bsub.py --threads 3 -q long 4 Passedf_201 \
    gatk --java-options "-Xmx4G" SelectVariants -R Ref_nohap/Sm_v7_nohap.fa -V Filtered_SNPs_201.vcf  --exclude-filtered -O Passedf_SNPs_201.vcf

# to look at and count the sample names
bcftools-1.5 query -l ExcludedFilteredSNPs_Indels.vcf | wc -l
bcftools-1.5 stats ExcludedFiltered_SNPs.vcf > excludedfilteredsnps.vcf
bcftools-1.5 stats subset.vcf.recode.vcf > Filtered_subset_recode.vcf

#Filtering the subset vcf from Duncan to use as my outgroup
gatk-4.1.0.0/gatk --java-options "-Xmx10G" SelectVariants -R Schistosoma_mansoni_v7.fa -V subset.vcf.recode.vcf --select-type-to-include SNP -O Outgroup_SNPs.vcf

bsub.py --threads 3 -q long 10 hardf201 gatk --java-options "-Xmx10G" VariantFiltration -R Ref_nohap/Sm_v7_nohap.fa -V 201_SNPs_new.vcf -O hardf.201_SNPs_new.vcf \
        --filterExpression "QD < 2.0 || MQ < 40.0 || FS > 60.0 || SOR > 3.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0" --filter-name "201.Filters_SNPs"

#for indels
gatk-4.1.0.0/gatk --java-options "-Xmx10G" SelectVariants -R Schistosoma_mansoni_v7.fa -V subset.vcf.recode.vcf--select-type-to-exclude SNP -O Outgroup_Indels.vcf

gatk-4.1.0.0/gatk --java-options "-Xmx10G" VariantFiltration -R Schistosoma_mansoni_v7.fa  -V Outgroup_Indels.vcf -O FilteredIndels_Outgroup.vcf \
                                    --filter-expression 'QD < 2 || ReadPosRankSum < -20.0 || InbreedingCoeff < -0.8 || FS > 200.0 || SOR > 10.0' --filter-name "OutgrpFiltersIndels"

gatk-4.1.0.0/gatk --java-options "-Xmx10G" VariantFiltration -R Ref_nohap/Sm_v7_nohap.fa -O hardf_21.SNPs.vcf --V Outgroup_Indels.vcf \
                                        --filter-expression 'QD < 2.0 || ReadPosRankSum < -20.0 || FS > 200.0 || SOR > 10.0 || InbreedingCoeff < -0.8' --filter-name "Filters_Indels"

#remove filtered snps and indels using the gatk exclude filtered option#
bsub.py --threads 3 -q normal 10 ExcludeFiltered_outgrpSNPs \
    gatk --java-options "-Xmx10G" SelectVariants -R Ref_nohap/Sm_v7_nohap.fa -V hardf.201_SNPs_new.vcf --exclude-filtered -O PASS.201_SNPs_new.vcf

bsub.py --threads 3 -q normal 10 ExcludeF_outgrpIndels gatk-4.1.0.0/gatk --java-options "-Xmx10G" SelectVariants -R Schistosoma_mansoni_v7.fa -V  FilteredIndels_Outgroup.vcf --exclude-filtered -O ExcludedFiltered_outgrpIndels.vcf

bsub.py --threads 3 -q normal 10 outgroup gatk-4.1.0.0/gatk --java-options "-Xmx10G" MergeVcfs -I ExcludedFiltered_outgrpIndels.vcf -I ExcludedFiltered_outgrpSNPS.vcf -O Clean_Outgroup.vcf

#merging two vcf files into one for my outgroup
vcfcat FilteredSNPs_outgroup.vcf FilteredIndels_Outgroup.vcf > Clean_Outgroup.vcf

vcfcat ExcludedFiltered_Merged.vcf Clean_Outgroup.vcf > Clean_Myvcf_Outgroup.vcf

#merging excluded filtered snps and indels for outgroup vcf#
bsub.py --threads 3 -q normal 10 mergecleanoutgrp vcfcat ExcludedFiltered_outgrpSNPS.vcf ExcludedFiltered_outgrpIndels.vcf > Clean_Outgroup.vcf

#The Fixation Index test
bsub.py --threads 3 -q normal 10 Std_Int_10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --weir-fst-pop Sample.lists/Standard.txt \
                                                  --weir-fst-pop Sample.lists/Intensive.txt --fst-window-size 10000 --out std_vs_Int_10k

bsub.py --threads 3 -q normal 10 TPt1_2_10kb ~jc17/software/vcftools_0.1.15/vcftools \
        --vcf Biallelic_clean_174.recode.vcf --weir-fst-pop ../../../Sample.lists/Tp1.txt \
                                                    --weir-fst-pop ../../../Sample.lists/Tp2.txt --fst-window-size 10000 --out Tpt1_vs_Tpt2_10kb

bsub.py --threads 3 -q normal 10 Damba_koome ~jc17/software/vcftools_0.1.15/vcftools \
                                             --vcf Biallelic_clean_174.recode.vcf --weir-fst-pop ../../../Sample.lists/Damba.txt \
                                             --weir-fst-pop ../../../Sample.lists/Koome.txt --fst-window-size 10000 --out Damba_vs_Koome_10kb

bsub.py --threads 3 -q long 4 pre_10kb ~jc17/software/vcftools_0.1.15/vcftools \
        --vcf Biallelic_clean_174.recode.vcf --weir-fst-pop ../../../Sample.lists/Pre_std.txt \
        --weir-fst-pop ../../../Sample.lists/Pre_int.txt --fst-window-size 10000 --out Pre_std.int_10kb

bsub.py --threads 3 -q long 4 post_10kb ~jc17/software/vcftools_0.1.15/vcftools \
        --vcf Biallelic_clean_174.recode.vcf --weir-fst-pop ../../../Sample.lists/Post_std.txt \
                                                            --weir-fst-pop ../../../Sample.lists/Post_int.txt --fst-window-size 10000 --out Post_std.int_10kb
# village fst # ci
bsub.py --threads 3 -q normal 4 Kakeeka_Kachanga ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kakeeka.txt --weir-fst-pop ../../../Sample.lists/Kachanga.txt --out Kakeeka_Kachanga

bsub.py --threads 3 -q normal 4 Zingola_Katooke ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Zingoola.txt --weir-fst-pop ../../../Sample.lists/Katooke.txt --out Zingoola_Katooke

bsub.py --threads 3 -q normal 4 Zingola_Kachanga ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Zingoola.txt --weir-fst-pop ../../../Sample.lists/Kachanga.txt --out Zingoola_Kachanga

bsub.py --threads 3 -q normal 4 Katooke_Kachanga ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Katooke.txt --weir-fst-pop ../../../Sample.lists/Kachanga.txt --out Katooke_Kachanga

bsub.py --threads 3 -q normal 4 Zingoola_Busi ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Busi.txt --weir-fst-pop ../../../Sample.lists/Zingoola.txt --out Zingoola_Busi

bsub.py --threads 3 -q normal 4 Kachanga_Busi ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Busi.txt --weir-fst-pop ../../../Sample.lists/Kachanga.txt --out Kachanga_Busi

bsub.py --threads 3 -q normal 4 Kachanga_Kisu ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kisu.txt --weir-fst-pop ../../../Sample.lists/Kachanga.txt --out Kachanga_Kisu

bsub.py --threads 3 -q normal 4 Katooke_Busi ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Busi.txt --weir-fst-pop ../../../Sample.lists/Katooke.txt --out Katooke_Busi

bsub.py --threads 3 -q normal 4 Katooke_Kisu ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kisu.txt --weir-fst-pop ../../../Sample.lists/Katooke.txt --out Katooke_Kisu

bsub.py --threads 3 -q normal 4 Zingoola_Kisu ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kisu.txt --weir-fst-pop ../../../Sample.lists/Zingoola.txt --out Zingoola_Kisu

bsub.py --threads 3 -q normal 4 Zingola_Kakeeka ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kakeeka.txt --weir-fst-pop ../../../Sample.lists/Zingoola.txt --out Zingoola_Kakeeka

bsub.py --threads 3 -q normal 4 Katooke_Lugumba ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Katooke.txt --weir-fst-pop ../../../Sample.lists/Lugumba.txt --out Katooke_Lugumba

bsub.py --threads 3 -q normal 4 zingoola_kitosi ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Zingoola.txt --weir-fst-pop ../../../Sample.lists/Kitosi.txt --out Kitosi_Zingoola

bsub.py --threads 3 -q normal 4 zingola_lugumba ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Zingoola.txt --weir-fst-pop ../../../Sample.lists/Lugumba.txt --out Lugumba_Zingoola

bsub.py --threads 3 -q normal 4 kakeeka_katooke ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kakeeka.txt --weir-fst-pop ../../../Sample.lists/Katooke.txt --out Kakeeka_Katooke

bsub.py --threads 3 -q normal 4 kitosi_katooke ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kitosi.txt --weir-fst-pop ../../../Sample.lists/Katooke.txt --out Kitosi_Katooke

bsub.py --threads 3 -q normal 4 busi_kakeeka ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Busi.txt --weir-fst-pop ../../../Sample.lists/Kakeeka.txt --out Kakeeka_Busi

bsub.py --threads 3 -q normal 4 kisu_kakeeka ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kisu.txt --weir-fst-pop ../../../Sample.lists/Kakeeka.txt --out Kakeeka_Kisu

bsub.py --threads 3 -q normal 4 lugumba_busi ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Lugumba.txt --weir-fst-pop ../../../Sample.lists/Busi.txt --out Busi_Lugumba

bsub.py --threads 3 -q normal 4 kisu_busi ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kisu.txt --weir-fst-pop ../../../Sample.lists/Busi.txt --out Busi_Kisu

bsub.py --threads 3 -q normal 4 kitosi_kachanga ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kitosi.txt --weir-fst-pop ../../../Sample.lists/Kachanga.txt --out Kitosi_Kachanga

bsub.py --threads 3 -q normal 4 kitosi_busi ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kitosi.txt --weir-fst-pop ../../../Sample.lists/Busi.txt --out Kitosi_Busi

bsub.py --threads 3 -q normal 4 kitosi_lugumba ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kitosi.txt --weir-fst-pop ../../../Sample.lists/Lugumba.txt --out Kitosi_Lugumba

bsub.py --threads 3 -q normal 4 kachanga_lugumba ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kachanga.txt --weir-fst-pop ../../../Sample.lists/Lugumba.txt --out Kachanga_Lugumba

bsub.py --threads 3 -q normal 4 kitosi_kisu ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kitosi.txt --weir-fst-pop ../../../Sample.lists/Kisu.txt --out Kitosi_Kisu

bsub.py --threads 3 -q normal 4 lugumba_kisu ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Lugumba.txt --weir-fst-pop ../../../Sample.lists/Kisu.txt --out Lugumba_Kisu

bsub.py --threads 3 -q normal 4 Kakeeka_kitosi ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kakeeka.txt --weir-fst-pop ../../../Sample.lists/Kitosi.txt --out Kakeeka_Kitosi

bsub.py --threads 3 -q normal 4 Kakeeka_lugumba ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf \
        --weir-fst-pop ../../../Sample.lists/Kakeeka.txt --weir-fst-pop ../../../Sample.lists/Lugumba.txt --out Kakeeka_Lugumba

#merging outgrp and myvcf#
bsub.py --threads 3 -q normal 10 mergingMyvcf_outgrp vcfcat ExcludedFiltered_Merged.vcf Clean_Outgroup.vcf > Clean_Myvcf_Outgroup.vcf #wrong command sticks vcfs ontop of each other
bsub.py --threads 3 -q normal 10 Merging_outgrp gatk-4.1.0.0/gatk --java-options "-Xmx10G" MergeVcfs -I /lustre/scratch118/infgen/team133/db22/software/bcftools-1.9/bcftools
vcfcat FilteredSNPs_outgroup.vcf FilteredIndels_Outgroup.vcf > Clean_Outgroup.vcf # vcfcat not good coz sticks vcf files onto of each other and hence now trying bcftools
bgzip -c ExcludedFiltered_outgrpIndels.vcf > FExcludedFiltered_outgrpIndels.vcf.gz
bgzip -c FilteredMissing_site_maf.recode.vcf > FilteredMissing_site_maf.recode.vcf.gz
bgzip -c Filtered_SNPs.vcf > Filtered_SNPs.vcf.gz

#merging indels and SNPs vcfs for the outgroup to create a clean outgroup#
/lustre/scratch118/infgen/team133/db22/software/bcftools-1.9/bcftools concat -a ExcludedFiltered_outgrpIndels.vcf.gz ExcludedFiltered_outgrpSNPS.vcf.gz -o Clean_Outgroup.vcf

#MERGING  outgroup with my vcf#
bgzip -c ExcludedFiltered_Merged.vcf > ExcludedFiltered_Merged.vcf.gz
bgzip -c Clean_Outgroup.vcf > Clean_Outgroup.vcf.gz

/lustre/scratch118/infgen/team133/db22/software/bcftools-1.9/bcftools index Clean_Outgroup.vcf.gz
/lustre/scratch118/infgen/team133/db22/software/bcftools-1.9/bcftools merge ExcludedFiltered_Merged.vcf.gz Clean_Outgroup.vcf.gz -o Clean_Myvcf_Outgroup.vcf

#calculating the distance matrices for tree with outgroup#
./plink --vcf FilteredMissing_site_maf_outgrp.recode.vcf --make-bed --out Variants_outgrp --allow-extra-chr --double-id
./plink2 --bfile Variants_outgrp --maf 0.01 --indep-pairwise 50 5 0.2

--allow-extra-chr --out Pruned_Variants_outgrp --set-all-var-ids @_#_
./plink2 --bfile Variants_outgrp --extract Pruned_Variants_outgrp.prune.in --allow-extra-chr --make-bed --out Pruned_extracted_Variants_outgrp --set-all-var-ids @_#_
./plink --bfile  Pruned_extracted_Variants_outgrp --distance square0 --allow-extra-chr --out Variants_tree_outgrp

#grabbing line with fewer tokens#
cat -n Clean_Myvcf_Outgroup.vcf | grep "15812818" > badline.txt
awk '! /\#/' Variants.vcf | awk '{if(length($4) > length($5)) print $1"\t"($2-1)"\t"($2+length($4)-1); else print $1"\t"($2-1)"\t"($2+length($5)-1)}' > Variants.bed

#grabbing a given command i typed in my command history
grep "login" ~jt24/.history/*

#indexing the vcf to be used in R for MK test
tabix -p vcf ExcludedFiltered_Merged.vcf.gz

#Ruuning MK test in R
bsub.py --threads 3 -q basement 10 MK_read_data   GENOME.class <- readData("VCF", format = "VCF")
bsub.py --threads 3 -q normal 10 MK_read_data ./MK.R
/software/R-3.1.2/bin/Rscript
/nfs/users/nfs_j/jc17/bin/MK.pl

#!/software/R-3.5.0/bin/Rscript#

#Computing Tajima's D
bsub.py --threads 3 -q long 10 td_50kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --maf 0.01 --TajimaD 50000 --out 50kb
bsub.py --threads 3 -q long 10 td_10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --maf 0.01 --TajimaD 10000 --out 10kb
bsub.py --threads 3 -q long 10 td_25kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --maf 0.01 --TajimaD 25000 --out 25kb

#Filtering for missingness
bsub.py --threads 3 -q long 4 174site_maf \
    ~jc17/software/vcftools_0.1.15/vcftools --vcf 174.only.Hfiltered.SNPs_new.vcf --recode --recode-INFO-all --max-missing 0.95 --maf 0.01 --out SNPs_174_site_maf_new

bsub.py --threads 3 -q normal 10 site_maf201 ~jc17/software/vcftools_0.1.15/vcftools --vcf PASS.201_SNPs_new.vcf --recode --recode-INFO-all --max-missing 0.95 --maf 0.01 --out Site_maf.201_SNPs_new

#calculating linkage disequilibrium for my merged vcf using r2 of 0.1
bsub.py --threads 3 -q normal 4 ld ~jc17/software/vcftools_0.1.15/vcftools \
                                                              --vcf FilteredMissing_site_maf_outgrp.recode.vcf --geno-r2 --min-r2 0.1 --ld-window-bp 10000 --out Merged_ld
bsub.py --threads 3 -q normal 4 ld \
    ~jc17/software/vcftools_0.1.15/vcftools --vcf FilteredMissing_site_maf_outgrp.recode.vcf --geno-r2 --min-r2 0.1 --ld-window-bp 100000 --out 100kb_ld

#Filtering-in only biallelic SNPs
bsub.py --threads 3 -q long 10 bi.174 \
    ~jc17/software/vcftools_0.1.15/vcftools --vcf SNPs_174_site_maf_new.recode.vcf --recode --recode-INFO-all --min-alleles 2 --max-alleles 2 --out Biallelic_174_new

bsub.py --threads 3 -q long 10 bi.201 \
    ~jc17/software/vcftools_0.1.15/vcftools --vcf Site_maf.201_SNPs_new.recode.vcf --recode --recode-INFO-all --min-alleles 2 --max-alleles 2 --out Bi_201_new

#making PCA from variants #Downloaded plink, used cyberduck to get it to farm and unzipped it 17/04/2019#
./plink --vcf FilteredMissing_site_maf.recode.vcf --make-bed --allow-extra-chr --out Variants
./plink2 --bfile Variants --maf 0.01 --indep-pairwise 50 5 0.2 --allow-extra-chr --out Pruned_Variants
./plink --vcf FilteredMissing_site_maf.recode.vcf --extract Pruned_Variants.prune.in --make-bed --allow-extra-chr --out Variants_extracted
./plink2 --bfile Variants_extracted --pca var-wts --allow-extra-chr  --out Variants_PCA #making PCA on clean bed file as used in tree above

./plink --vcf Biallelic_174_new.recode.vcf --make-bed --allow-extra-chr --out PCA_174
./plink2 --bfile PCA_174 --maf 0.01 --indep-pairwise 50 5 0.2 --allow-extra-chr --out Pruned_174
./plink --vcf Biallelic_174_new.recode.vcf --extract Pruned_174.prune.in --make-bed --allow-extra-chr --out PCA_174_extracted
./plink2 --bfile PCA_174_extracted --pca var-wts --allow-extra-chr --out PCAs_174

./plink --vcf Bi_201_new.recode.vcf --make-bed --allow-extra-chr --out PCA_201
./plink2 --bfile PCA_201 --maf 0.01 --indep-pairwise 50 5 0.2 --allow-extra-chr --out Pruned_201
./plink --vcf Bi_201_new.recode.vcf --extract Pruned_201.prune.in --make-bed --allow-extra-chr --out PCA_201_extracted
./plink2 --bfile PCA_201_extracted --pca var-wts --allow-extra-chr --out PCAs_201

#making pca with outgroup#
./plink2 --bfile Pruned_Myvcf_Outgrpbed_extracted --pca var-wts --allow-extra-chr  --out Myvcf_outgrp_PCA

#copying list.txt files from computer to directory in cluster
mib111164i:~ jt24$ pwd  # get current working directory
/Users/jt24 # printed wd
cd Desktop/NovaSeq_data_analysis/ #*** move to folder on pc where the files are saved
/lustre/scratch118/infgen/team133/jt24/VariantCalling_finished/CLEAN_VCFs #copy directory on the cluster/ file path where i want to put the list.txt files
scp List*.txt seq3://lustre/scratch118/infgen/team133/jt24/VariantCalling_finished/CLEAN_VCFs #command to move the files from home pc to cluster folder specified :)
#prompt to confirm making the transfer, reply yes, enter password and its done :) #

#Making phylogenetic tree
./plink --vcf FilteredMissing_site_maf_outgrp.recode.vcf --make-bed --allow-extra-chr --out Variants_outgrp --set-all-var-ids @_#_
./plink2 --bfile Variants --maf 0.01 --indep-pairwise 50 5 0.2 --allow-extra-chr --out Pruned_Variants --set-all-var-ids @_#_
./plink2 --bfile Variants --extract Pruned_Variants.prune.in --allow-extra-chr --make-bed --out Pruned_extracted_Variants --set-all-var-ids @_#_
./plink --bfile  Pruned_extracted_Variants --distance square0  --allow-extra-chr --out Variants_tree  # MAKE bed, prune bed, extract bed and calculate distance matrix to make phylogenetic tree

./plink --vcf Biallelic_174_new.recode.vcf --make-bed --allow-extra-chr --out Tree_174
./plink2 --bfile Tree_174 --maf 0.01 --indep-pairwise 50 5 0.2 --allow-extra-chr --out 174
./plink2 --bfile Tree_174 --extract 174.prune.in --allow-extra-chr --make-bed --out Extracted_174
./plink --bfile  Extracted_174 --distance square0  --allow-extra-chr --out 174_tree

./plink --vcf Passedf_SNPs_201_site_maf.recode.vcf --make-bed --allow-extra-chr --out Variants_201
./plink2 --bfile Variants_201 --maf 0.01 --indep-pairwise 50 5 0.2 --allow-extra-chr --out 201
./plink2 --bfile Variants_201 --extract 201.prune.in --allow-extra-chr --make-bed --out Extracted_201
./plink --bfile  Extracted_201 --distance square0  --allow-extra-chr --out 201_tree

#converting vcf to ped
~jc17/software/vcftools_0.1.15/vcftools --vcf FilteredMissing_site_maf.recode.vcf --out my_ped --plink

#Remove haplotypes from vcf using vcftools
bsub.py --threads 3 -q long 10 cleanbi ~jc17/software/vcftools_0.1.15/vcftools --vcf Biallelic_174_new.recode.vcf \
        --chr "SM_V7_1"  --chr "SM_V7_2" --chr "SM_V7_3" --chr "SM_V7_4" --chr "SM_V7_5" --chr "SM_V7_6" --chr "SM_V7_7" --chr "SM_V7_ZW" \
                                                                                      --recode --recode-INFO-all --out Biallelic_clean_174

bsub.py --threads 3 -q yesterday 10 std.nohap ~jc17/software/vcftools_0.1.15/vcftools \
            --vcf Std.recode.vcf --chr "SM_V7_1_1"  --chr "SM_V7_2_4" --chr "SM_V7_3_3" --chr "SM_V7_4_5" --chr "SM_V7_5_6" --chr "SM_V7_6_7" --chr "SM_V7_7_8" --chr "SM_V7_ZW_2" \
                                                    --recode --recode-INFO-all --out Std_nohap.recode.vcf

bsub.py --threads 3 -q yesterday 10 int.nohap ~jc17/software/vcftools_0.1.15/vcftools \
            --vcf Int.recode.vcf --chr "SM_V7_1_1"  --chr "SM_V7_2_4" --chr "SM_V7_3_3" --chr "SM_V7_4_5" --chr "SM_V7_5_6" --chr "SM_V7_6_7" --chr "SM_V7_7_8" --chr "SM_V7_ZW_2" \
                                                    --recode --recode-INFO-all --out Int_nohap.recode.vcf

bsub.py --threads 3 -q long 10 tp1.nohap ~jc17/software/vcftools_0.1.15/vcftools \
            --vcf Tp1.recode.vcf --chr "SM_V7_1_1"  --chr "SM_V7_2_4" --chr "SM_V7_3_3" --chr "SM_V7_4_5" --chr "SM_V7_5_6" --chr "SM_V7_6_7" --chr "SM_V7_7_8" --chr "SM_V7_ZW_2" \
                                                    --recode --recode-INFO-all --out Tp1_nohap.recode.vcf

bsub.py --threads 3 -q long 10 tp2.nohap ~jc17/software/vcftools_0.1.15/vcftools \
            --vcf Tp2.recode.vcf --chr "SM_V7_1_1"  --chr "SM_V7_2_4" --chr "SM_V7_3_3" --chr "SM_V7_4_5" --chr "SM_V7_5_6" --chr "SM_V7_6_7" --chr "SM_V7_7_8" --chr "SM_V7_ZW_2" \
                                                    --recode --recode-INFO-all --out Tp2_nohap.recode.vcf

#Spliting the vcf into individual chromosomes#
bsub.py --threads 3 -q long 4 SplitChr1 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --chr "SM_V7_1" --recode --recode-INFO-all --out Bi_174_chr1
bsub.py --threads 3 -q long 4 SplitChr2 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --chr "SM_V7_2" --recode --recode-INFO-all --out Bi_174_chr2
bsub.py --threads 3 -q long 4 SplitChr3 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --chr "SM_V7_3" --recode --recode-INFO-all --out Bi_174_chr3
bsub.py --threads 3 -q long 4 SplitChr4 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --chr "SM_V7_4" --recode --recode-INFO-all --out Bi_174_chr4
bsub.py --threads 3 -q long 4 SplitChr5 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --chr "SM_V7_5" --recode --recode-INFO-all --out Bi_174_chr5
bsub.py --threads 3 -q long 4 SplitChr6 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --chr "SM_V7_6" --recode --recode-INFO-all --out Bi_174_chr6
bsub.py --threads 3 -q long 4 SplitChr7 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --chr "SM_V7_7" --recode --recode-INFO-all --out Bi_174_chr7
bsub.py --threads 3 -q long 4 SplitChrZW ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --chr "SM_V7_ZW" --recode --recode-INFO-all --out Bi_174_chrZW

#phasing haplotypes#
#got errors because of a single dot and i solved it by using cat  Biallelic_174_new.recode.vcf | perl -pe "s/\s\.:/\t.\/.:/g" >  Bi_174_new.recode.vcf
#this created a vcf to use to phase the genotypes#
bsub.py --threads 3 -q basement 15 phaseChr1 java -Xmx15g -jar beagle.16May19.351.jar.1 gt=Bi_174_chr1.recode.vcf nthreads=3 map=Chr1_mp.txt out=Chr1_174_phased
bsub.py --threads 3 -q basement 15 phaseChr2 java -Xmx15g -jar beagle.16May19.351.jar.1 gt=Bi_174_chr2.recode.vcf nthreads=3 map=Chr2_mp.txt out=Chr2_174_phased
bsub.py --threads 3 -q basement 15 phaseChr3 java -Xmx15g -jar beagle.16May19.351.jar.1 gt=Bi_174_chr3.recode.vcf nthreads=3 map=Chr3_mp.txt out=Chr3_174_phased
bsub.py --threads 3 -q basement 15 phaseChr4 java -Xmx15g -jar beagle.16May19.351.jar.1 gt=Bi_174_chr4.recode.vcf nthreads=3 map=Chr4_mp.txt out=Chr4_174_phased
bsub.py --threads 3 -q basement 15 phaseChr5 java -Xmx15g -jar beagle.16May19.351.jar.1 gt=Bi_174_chr5.recode.vcf nthreads=3 map=Chr5_mp.txt out=Chr5_174_phased
bsub.py --threads 3 -q basement 15 phaseChr6 java -Xmx15g -jar beagle.16May19.351.jar.1 gt=Bi_174_chr6.recode.vcf nthreads=3 map=Chr6_mp.txt out=Chr6_174_phased
bsub.py --threads 3 -q basement 15 phaseChr7 java -Xmx15g -jar beagle.16May19.351.jar.1 gt=Bi_174_chr7.recode.vcf nthreads=3 map=Chr7_mp.txt out=Chr7_174_phased
bsub.py --threads 3 -q basement 15 phaseChrZW java -Xmx15g -jar beagle.16May19.351.jar.1 gt=Bi_174_chrZW.recode.vcf nthreads=3 map=ChrZW_mp.txt out=ChrZW_174_phased

#SELSCAN#selecting std samples on chromosomes#
bsub.py --threads 3 -q normal 4 chr1std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr1_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Standard.txt --out Chr1_std
bsub.py --threads 3 -q normal 4 chr1int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr1_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Intensive.txt --out Chr1_int
bsub.py --threads 3 -q normal 4 chr1tp1 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr1_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp1.txt --out Chr1_tp1
bsub.py --threads 3 -q normal 4 chr1tp2 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr1_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp2.txt --out Chr1_tp2
bsub.py --threads 3 -q normal 4 chr2std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr2_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Standard.txt --out Chr2_std
bsub.py --threads 3 -q normal 4 chr2int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr2_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Intensive.txt --out Chr2_int
bsub.py --threads 3 -q normal 4 chr2tp1 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr2_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp1.txt --out Chr2_tp1
bsub.py --threads 3 -q normal 4 chr2tp2 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr2_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp2.txt --out Chr2_tp2
bsub.py --threads 3 -q normal 4 chr3std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr3_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Standard.txt --out Chr3_std
bsub.py --threads 3 -q normal 4 chr3int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr3_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Intensive.txt --out Chr3_int
bsub.py --threads 3 -q normal 4 chr3tp1 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr3_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp1.txt --out Chr3_tp1
bsub.py --threads 3 -q normal 4 chr3tp2 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr3_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp2.txt --out Chr3_tp2
bsub.py --threads 3 -q normal 4 chr4std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr4_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Standard.txt --out Chr4_std
bsub.py --threads 3 -q normal 4 chr4int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr4_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Intensive.txt --out Chr4_int
bsub.py --threads 3 -q normal 4 chr4tp1 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr4_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp1.txt --out Chr4_tp1
bsub.py --threads 3 -q normal 4 chr4tp2 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr4_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp2.txt --out Chr4_tp2
bsub.py --threads 3 -q normal 4 chr5std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr5_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Standard.txt --out Chr5_std
bsub.py --threads 3 -q normal 4 chr5int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr5_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Intensive.txt --out Chr5_int
bsub.py --threads 3 -q normal 4 chr5tp1 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr5_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp1.txt --out Chr5_tp1
bsub.py --threads 3 -q normal 4 chr5tp2 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr5_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp2.txt --out Chr5_tp2
bsub.py --threads 3 -q normal 4 chr6std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr6_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Standard.txt --out Chr6_std
bsub.py --threads 3 -q normal 4 chr6int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr6_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Intensive.txt --out Chr6_int
bsub.py --threads 3 -q normal 4 chr6tp1 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr6_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp1.txt --out Chr6_tp1
bsub.py --threads 3 -q normal 4 chr6tp2 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr6_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp2.txt --out Chr6_tp2
bsub.py --threads 3 -q normal 4 chr7std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr7_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Standard.txt --out Chr7_std
bsub.py --threads 3 -q normal 4 chr7int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr7_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Intensive.txt --out Chr7_int
bsub.py --threads 3 -q normal 4 chr7tp1 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr7_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp1.txt --out Chr7_tp1
bsub.py --threads 3 -q normal 4 chr7tp2 ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr7_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp2.txt --out Chr7_tp2
bsub.py --threads 3 -q normal 4 chrzwstd ~jc17/software/vcftools_0.1.15/vcftools --vcf ChrZW_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Standard.txt --out ChrZW_std
bsub.py --threads 3 -q normal 4 chrzwint ~jc17/software/vcftools_0.1.15/vcftools --vcf ChrZW_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Intensive.txt --out ChrZW_int
bsub.py --threads 3 -q normal 4 chrzwtp1 ~jc17/software/vcftools_0.1.15/vcftools --vcf ChrZW_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp1.txt --out ChrZW_tp1
bsub.py --threads 3 -q normal 4 chrzwtp2 ~jc17/software/vcftools_0.1.15/vcftools --vcf ChrZW_174_phased.vcf --recode --recode-INFO-all --keep Sample.lists/Tp2.txt --out ChrZW_tp2

#calculating IHS using selscan#
bsub.py --threads 3 -q normal 15 ihsChr1_std selscan/bin/linux/selscan --ihs --vcf Chr1_std.recode.vcf --map Chr1_mp.txt --out iHS_Chr1_std
bsub.py --threads 3 -q normal 15 ihsChr1_int selscan/bin/linux/selscan --ihs --vcf Chr1_int.recode.vcf --map Chr1_mp.txt --out iHS_chr1_int
bsub.py --threads 3 -q normal 15 ihsChr1_tp1 selscan/bin/linux/selscan --ihs --vcf Chr1_tp1.recode.vcf --map Chr1_mp.txt --out iHS_chr1_tp1
bsub.py --threads 3 -q normal 15 ihsChr1_tp2 selscan/bin/linux/selscan --ihs --vcf Chr1_tp2.recode.vcf --map Chr1_mp.txt --out iHS_chr1_tp2
bsub.py --threads 3 -q normal 15 ihsChr2_std selscan/bin/linux/selscan --ihs --vcf Chr2_std.recode.vcf --map Chr2_mp.txt --out iHS_Chr2_std
bsub.py --threads 3 -q normal 15 ihsChr2_int selscan/bin/linux/selscan --ihs --vcf Chr2_int.recode.vcf --map Chr2_mp.txt --out iHS_chr2_int
bsub.py --threads 3 -q normal 15 ihsChr2_tp1 selscan/bin/linux/selscan --ihs --vcf Chr2_tp1.recode.vcf --map Chr2_mp.txt --out iHS_chr2_tp1
bsub.py --threads 3 -q normal 15 ihsChr2_tp2 selscan/bin/linux/selscan --ihs --vcf Chr2_tp2.recode.vcf --map Chr2_mp.txt --out iHS_chr2_tp2
bsub.py --threads 3 -q normal 15 ihsChr3_std selscan/bin/linux/selscan --ihs --vcf Chr3_std.recode.vcf --map Chr3_mp.txt --out iHS_Chr3_std
bsub.py --threads 3 -q normal 15 ihsChr3_int selscan/bin/linux/selscan --ihs --vcf Chr3_int.recode.vcf --map Chr3_mp.txt --out iHS_chr3_int
bsub.py --threads 3 -q normal 15 ihsChr3_tp1 selscan/bin/linux/selscan --ihs --vcf Chr3_tp1.recode.vcf --map Chr3_mp.txt --out iHS_chr3_tp1
bsub.py --threads 3 -q normal 15 ihsChr3_tp2 selscan/bin/linux/selscan --ihs --vcf Chr3_tp2.recode.vcf --map Chr3_mp.txt --out iHS_chr3_tp2
bsub.py --threads 3 -q normal 15 ihsChr4_std selscan/bin/linux/selscan --ihs --vcf Chr4_std.recode.vcf --map Chr4_mp.txt --out iHS_Chr4_std
bsub.py --threads 3 -q normal 15 ihsChr4_int selscan/bin/linux/selscan --ihs --vcf Chr4_int.recode.vcf --map Chr4_mp.txt --out iHS_chr4_int
bsub.py --threads 3 -q normal 15 ihsChr4_tp1 selscan/bin/linux/selscan --ihs --vcf Chr4_tp1.recode.vcf --map Chr4_mp.txt --out iHS_chr4_tp1
bsub.py --threads 3 -q normal 15 ihsChr4_tp2 selscan/bin/linux/selscan --ihs --vcf Chr4_tp2.recode.vcf --map Chr4_mp.txt --out iHS_chr4_tp2
bsub.py --threads 3 -q normal 15 ihsChr5_std selscan/bin/linux/selscan --ihs --vcf Chr5_std.recode.vcf --map Chr5_mp.txt --out iHS_Chr5_std
bsub.py --threads 3 -q normal 15 ihsChr5_int selscan/bin/linux/selscan --ihs --vcf Chr5_int.recode.vcf --map Chr5_mp.txt --out iHS_chr5_int
bsub.py --threads 3 -q normal 15 ihsChr5_tp1 selscan/bin/linux/selscan --ihs --vcf Chr5_tp1.recode.vcf --map Chr5_mp.txt --out iHS_chr5_tp1
bsub.py --threads 3 -q normal 15 ihsChr5_tp2 selscan/bin/linux/selscan --ihs --vcf Chr5_tp2.recode.vcf --map Chr5_mp.txt --out iHS_chr5_tp2
bsub.py --threads 3 -q normal 15 ihsChr6_std selscan/bin/linux/selscan --ihs --vcf Chr6_std.recode.vcf --map Chr6_mp.txt --out iHS_Chr6_std
bsub.py --threads 3 -q normal 15 ihsChr6_int selscan/bin/linux/selscan --ihs --vcf Chr6_int.recode.vcf --map Chr6_mp.txt --out iHS_chr6_int
bsub.py --threads 3 -q normal 15 ihsChr6_tp1 selscan/bin/linux/selscan --ihs --vcf Chr6_tp1.recode.vcf --map Chr6_mp.txt --out iHS_chr6_tp1
bsub.py --threads 3 -q normal 15 ihsChr6_tp2 selscan/bin/linux/selscan --ihs --vcf Chr6_tp2.recode.vcf --map Chr6_mp.txt --out iHS_chr6_tp2
bsub.py --threads 3 -q normal 15 ihsChr7_std selscan/bin/linux/selscan --ihs --vcf Chr7_std.recode.vcf --map Chr7_mp.txt --out iHS_Chr7_std
bsub.py --threads 3 -q normal 15 ihsChr7_int selscan/bin/linux/selscan --ihs --vcf Chr7_int.recode.vcf --map Chr7_mp.txt --out iHS_chr7_int
bsub.py --threads 3 -q normal 15 ihsChr7_tp1 selscan/bin/linux/selscan --ihs --vcf Chr7_tp1.recode.vcf --map Chr7_mp.txt --out iHS_chr7_tp1
bsub.py --threads 3 -q normal 15 ihsChr7_tp2 selscan/bin/linux/selscan --ihs --vcf Chr7_tp2.recode.vcf --map Chr7_mp.txt --out iHS_chr7_tp2
bsub.py --threads 3 -q normal 15 ihsChrZW_std selscan/bin/linux/selscan --ihs --vcf ChrZW_std.recode.vcf --map ChrZW_mp.txt --out iHS_ChrZW_std
bsub.py --threads 3 -q normal 15 ihsChrZW_int selscan/bin/linux/selscan --ihs --vcf ChrZW_int.recode.vcf --map ChrZW_mp.txt --out iHS_chrZW_int
bsub.py --threads 3 -q normal 15 ihsChrZW_tp1 selscan/bin/linux/selscan --ihs --vcf ChrZW_tp1.recode.vcf --map ChrZW_mp.txt --out iHS_chrZW_tp1
bsub.py --threads 3 -q normal 15 ihsChrZW_tp2 selscan/bin/linux/selscan --ihs --vcf ChrZW_tp2.recode.vcf --map ChrZW_mp.txt --out iHS_chrZW_tp2

# calculating XP-EHH using Selscan#
selscan/bin/linux/selscan --xpehh --gzvcf ExcludedFiltered_Merged.vcf  --vcf-ref /Ref/Schistosoma_mansoni_v7.fa --map Merged_plink --skip-low-freq --out Variant_xpehh

#making a genetic map with all sites included#
cut Bi_174_chr1.recode.vcf -f 1,2,3  > map_chr1
cut Bi_174_chr2.recode.vcf -f 1,2,3  > map_chr2
cut Bi_174_chr3.recode.vcf -f 1,2,3  > map_chr3
cut Bi_174_chr4.recode.vcf -f 1,2,3  > map_chr4
cut Bi_174_chr5.recode.vcf -f 1,2,3  > map_chr5
cut Bi_174_chr6.recode.vcf -f 1,2,3  > map_chr6
cut Bi_174_chr7.recode.vcf -f 1,2,3  > map_chr7
cut Bi_174_chrZW.recode.vcf -f 1,2,3  > map_chrZW

# XP - EHH#
bsub.py --threads 3 -q long 15 Chr1_std_int selscan/bin/linux/selscan --xpehh --vcf Chr1_std.recode.vcf --vcf-ref Chr1_int.recode.vcf --map Chr1_mp.txt --out Chr1_Std_Int
bsub.py --threads 3 -q long 15 Chr1_tp1_tp2 selscan/bin/linux/selscan --xpehh --vcf Chr1_tp1.recode.vcf --vcf-ref Chr1_tp2.recode.vcf --map Chr1_mp.txt --out Chr1_Tp1_Tp2
bsub.py --threads 3 -q long 15 Chr2_std_int selscan/bin/linux/selscan --xpehh --vcf Chr2_std.recode.vcf --vcf-ref Chr2_int.recode.vcf --map Chr2_mp.txt --out Chr2_Std_Int
bsub.py --threads 3 -q long 15 Chr2_tp1_tp2 selscan/bin/linux/selscan --xpehh --vcf Chr2_tp1.recode.vcf --vcf-ref Chr2_tp2.recode.vcf --map Chr2_mp.txt --out Chr2_Tp1_Tp2
bsub.py --threads 3 -q long 15 Chr3_std_int selscan/bin/linux/selscan --xpehh --vcf Chr3_std.recode.vcf --vcf-ref Chr3_int.recode.vcf --map Chr3_mp.txt --out Chr3_Std_Int
bsub.py --threads 3 -q long 15 Chr3_tp1_tp2 selscan/bin/linux/selscan --xpehh --vcf Chr3_tp1.recode.vcf --vcf-ref Chr3_tp2.recode.vcf --map Chr3_mp.txt --out Chr3_Tp1_Tp2
bsub.py --threads 3 -q long 15 Chr4_std_int selscan/bin/linux/selscan --xpehh --vcf Chr4_std.recode.vcf --vcf-ref Chr4_int.recode.vcf --map Chr4_mp.txt --out Chr4_Std_Int
bsub.py --threads 3 -q long 15 Chr4_tp1_tp2 selscan/bin/linux/selscan --xpehh --vcf Chr4_tp1.recode.vcf --vcf-ref Chr4_tp2.recode.vcf --map Chr4_mp.txt --out Chr4_Tp1_Tp2
bsub.py --threads 3 -q long 15 Chr5_std_int selscan/bin/linux/selscan --xpehh --vcf Chr5_std.recode.vcf --vcf-ref Chr5_int.recode.vcf --map Chr5_mp.txt --out Chr5_Std_Int
bsub.py --threads 3 -q long 15 Chr5_tp1_tp2 selscan/bin/linux/selscan --xpehh --vcf Chr5_tp1.recode.vcf --vcf-ref Chr5_tp2.recode.vcf --map Chr5_mp.txt --out Chr5_Tp1_Tp2
bsub.py --threads 3 -q long 15 Chr6_std_int selscan/bin/linux/selscan --xpehh --vcf Chr6_std.recode.vcf --vcf-ref Chr6_int.recode.vcf --map Chr6_mp.txt --out Chr6_Std_Int
bsub.py --threads 3 -q long 15 Chr6_tp1_tp2 selscan/bin/linux/selscan --xpehh --vcf Chr6_tp1.recode.vcf --vcf-ref Chr6_tp2.recode.vcf --map Chr6_mp.txt --out Chr6_Tp1_Tp2
bsub.py --threads 3 -q long 15 Chr7_std_int selscan/bin/linux/selscan --xpehh --vcf Chr7_std.recode.vcf --vcf-ref Chr7_int.recode.vcf --map Chr7_mp.txt --out Chr7_Std_Int
bsub.py --threads 3 -q long 15 Chr7_tp1_tp2 selscan/bin/linux/selscan --xpehh --vcf Chr7_tp1.recode.vcf --vcf-ref Chr7_tp2.recode.vcf --map Chr7_mp.txt --out Chr7_Tp1_Tp2
bsub.py --threads 3 -q long 15 ChrZW_std_int selscan/bin/linux/selscan --xpehh --vcf ChrZW_std.recode.vcf --vcf-ref ChrZW_int.recode.vcf --map ChrZW_mp.txt --out ChrZW_Std_Int
bsub.py --threads 3 -q long 15 ChrZW_tp1_tp2 selscan/bin/linux/selscan --xpehh --vcf ChrZW_tp1.recode.vcf --vcf-ref ChrZW_tp2.recode.vcf --map ChrZW_mp.txt --out ChrZW_Tp1_Tp2

# subseting tp2 for tp2 xpehh
bsub.py --threads 3 -q long 4 c1_t2.std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr1_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std_51.txt --out c1_t2.std
bsub.py --threads 3 -q long 4 c1_t2.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr1_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int_51.txt --out c1_t2.int
bsub.py --threads 3 -q long 4 c2_t2.std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr2_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std_51.txt --out c2_t2.std
bsub.py --threads 3 -q long 4 c2_t2.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr2_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int_51.txt --out c2_t2.int
bsub.py --threads 3 -q long 4 c3_t2.std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr3_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std_51.txt --out c3_t2.std
bsub.py --threads 3 -q long 4 c3_t2.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr3_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int_51.txt --out c3_t2.int
bsub.py --threads 3 -q long 4 c4_t2.std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr4_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std_51.txt --out c4_t2.std
bsub.py --threads 3 -q long 4 c4_t2.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr4_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int_51.txt --out c4_t2.int
bsub.py --threads 3 -q long 4 c5_t2.std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr5_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std_51.txt --out c5_t2.std
bsub.py --threads 3 -q long 4 c5_t2.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr5_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int_51.txt --out c5_t2.int
bsub.py --threads 3 -q long 4 c6_t2.std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr6_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std_51.txt --out c6_t2.std
bsub.py --threads 3 -q long 4 c6_t2.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr6_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int_51.txt --out c6_t2.int
bsub.py --threads 3 -q long 4 c7_t2.std ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr7_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std_51.txt --out c7_t2.std
bsub.py --threads 3 -q long 4 c7_t2.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Chr7_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int_51.txt --out c7_t2.int
bsub.py --threads 3 -q long 4 czw_t2.std ~jc17/software/vcftools_0.1.15/vcftools --vcf ChrZW_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std_51.txt --out czw_t2.std
bsub.py --threads 3 -q long 4 czw_t2.int ~jc17/software/vcftools_0.1.15/vcftools --vcf ChrZW_tp2.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int_51.txt --out czw_t2.int

#xpehh for post_std.int
bsub.py --threads 3 -q long 5 c1.t2_std.int selscan/bin/linux/selscan --xpehh --vcf c1_t2.std.recode.vcf --vcf-ref c1_t2.int.recode.vcf --map genetic_map/Chr1_mp.txt --out c1.t2_std.int
bsub.py --threads 3 -q long 5 c2.t2_std.int selscan/bin/linux/selscan --xpehh --vcf c2_t2.std.recode.vcf --vcf-ref c2_t2.int.recode.vcf --map genetic_map/Chr2_mp.txt --out c2.t2_std.int
bsub.py --threads 3 -q long 5 c3.t2_std.int selscan/bin/linux/selscan --xpehh --vcf c3_t2.std.recode.vcf --vcf-ref c3_t2.int.recode.vcf --map genetic_map/Chr3_mp.txt --out c3.t2_std.int
bsub.py --threads 3 -q long 5 c4.t2_std.int selscan/bin/linux/selscan --xpehh --vcf c4_t2.std.recode.vcf --vcf-ref c4_t2.int.recode.vcf --map genetic_map/Chr4_mp.txt --out c4.t2_std.int
bsub.py --threads 3 -q normal 5 c5.t2_std.int selscan/bin/linux/selscan --xpehh --vcf c5_t2.std.recode.vcf --vcf-ref c5_t2.int.recode.vcf --map genetic_map/Chr5_mp.txt --out c5.t2_std.int
bsub.py --threads 3 -q normal 5 c6.t2_std.int selscan/bin/linux/selscan --xpehh --vcf c6_t2.std.recode.vcf --vcf-ref c6_t2.int.recode.vcf --map genetic_map/Chr6_mp.txt --out c6.t2_std.int
bsub.py --threads 3 -q long 5 c7.t2_std.int selscan/bin/linux/selscan --xpehh --vcf c7_t2.std.recode.vcf --vcf-ref c7_t2.int.recode.vcf --map genetic_map/Chr7_mp.txt --out c7.t2_std.int
bsub.py --threads 3 -q long 5 czw.t2_std.int selscan/bin/linux/selscan --xpehh --vcf czw_t2.std.recode.vcf --vcf-ref czw_t2.int.recode.vcf --map genetic_map/ChrZW_mp.txt --out czw.t2_std.int

grep 'Success' *.o  #grabbing successful jobs

#Normalisation of ihs and xpehh scores#
ls *tp2.ihs.out

selscan/bin/linux/norm --ihs --files iHS_Chr1_std.ihs.out iHS_Chr2_std.ihs.out iHS_Chr3_std.ihs.out iHS_Chr4_std.ihs.out iHS_Chr5_std.ihs.out iHS_Chr6_std.ihs.out iHS_Chr7_std.ihs.out iHS_ChrZW_std.ihs.out
selscan/bin/linux/norm --ihs --files iHS_chr1_int.ihs.out iHS_chr2_int.ihs.out iHS_chr3_int.ihs.out iHS_chr4_int.ihs.out iHS_chr5_int.ihs.out iHS_chr6_int.ihs.out iHS_chr7_int.ihs.out iHS_chrZW_int.ihs.out
selscan/bin/linux/norm --ihs --files iHS_chr1_tp1.ihs.out iHS_chr2_tp1.ihs.out iHS_chr3_tp1.ihs.out iHS_chr4_tp1.ihs.out iHS_chr5_tp1.ihs.out iHS_chr6_tp1.ihs.out iHS_chr7_tp1.ihs.out iHS_chrZW_tp1.ihs.out
selscan/bin/linux/norm --ihs --files iHS_chr1_tp2.ihs.out iHS_chr2_tp2.ihs.out iHS_chr3_tp2.ihs.out iHS_chr4_tp2.ihs.out iHS_chr5_tp2.ihs.out iHS_chr6_tp2.ihs.out iHS_chr7_tp2.ihs.out iHS_chrZW_tp2.ihs.out

ls *_Tp1_Tp2.xpehh.out
selscan/bin/linux/norm --xpehh --files Chr1_Std_Int.xpehh.out Chr2_Std_Int.xpehh.out Chr3_Std_Int.xpehh.out Chr4_Std_Int.xpehh.out Chr5_Std_Int.xpehh.out Chr6_Std_Int.xpehh.out Chr7_Std_Int.xpehh.out ChrZW_Std_Int.xpehh.out
selscan/bin/linux/norm --xpehh --files Chr1_Tp1_Tp2.xpehh.out Chr2_Tp1_Tp2.xpehh.out Chr3_Tp1_Tp2.xpehh.out Chr4_Tp1_Tp2.xpehh.out Chr5_Tp1_Tp2.xpehh.out Chr6_Tp1_Tp2.xpehh.out Chr7_Tp1_Tp2.xpehh.out ChrZW_Tp1_Tp2.xpehh.out
selscan/bin/linux/norm --xpehh --files c1.t2_std.int.xpehh.out c2.t2_std.int.xpehh.out c3.t2_std.int.xpehh.out c4.t2_std.int.xpehh.out c5.t2_std.int.xpehh.out c6.t2_std.int.xpehh.out c7.t2_std.int.xpehh.out czw.t2_std.int.xpehh.out

#zipping large files#
bsub.py --threads 3 -q long 10 zip201 gzip -c combined_VIANNEY_201.vcf --name combined_VIANNEY_201.vcf.gz
bsub.py --threads 3 -q basement 4 zipg.vcf201 gzip -c combined_VIANNEY_201.g.vcf --name combined_VIANNEY_201.g.vcf.gz

# snpEff Annotation #
java -Xmx4g -jar snpEff.jar -v GRCh37.75 examples/test.chr22.vcf > test.chr22.ann.vcf
java -jar snpeff/snpEff/snpEff.jar databases | less
java -jar snpeff/snpEff/snpEff.jar databases | grep -i Schistosoma

bsub.py --threads 3 -q long 15 snps_eff java -Xmx15g -jar snpEff.jar eff -c snpEff.SC.config Sm_v7.2_Basic Bi_174_new.recode.vcf > 174_new.ann.vcf  #Right command

/lustre/scratch118/infgen/team133/db22/software/snpEff/data/Sm_v7.2_Basic/ #* name of schisto dabase created fro v7 "Sm_v7.2_Basic"
SMAN  genome, version 7

#Filtering sites by linkage disequilibrium
bcftools +prune Biallelic_SNPs_174_JVT.vcf -l 0.2 --window 10000 -O Biallelic_SNPs.ld_174_JVT.vcf

#Sm_v7.2_Basic.genome :Schistosoma mansoni
#data_dir = /lustre/scratch118/infgen/team133/jt24/snpeff/snpEff/data/Sm_v7.2_Basic/ # location of the genetic map database used
#snpSift filtering
# Regions under selection, std.int #
bsub.py --threads 3 -q normal 4 tv9 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 250001) & (POS < 275000)" -file  > TV9.vcf
bsub.py --threads 3 -q long 4 tv.148 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 3950001) & (POS < 3975000)" > tv_148.vcf
bsub.py --threads 3 -q long 4 tv745_746 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 19550001) & (POS < 19600000)" > TV_745_746.vcf
bsub.py --threads 3 -q long 4 1037 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "( CHROM = 'SM_V7_1' )" | java -jar SnpSift.jar filter "(POS > 27025001) & (POS < 27050000)" > 1037.vcf
bsub.py --threads 3 -q long 4 1080 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 27875001) & (POS < 28150000)" > tv_1080.vcf
bsub.py --threads 3 -q long 4 1214 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 31500001) & (POS < 31525000)" > tv_1214.vcf
bsub.py --threads 3 -q long 4 1414 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 36575001) & (POS < 36600000)" > 1414.vcf
bsub.py --threads 3 -q long 4 1613 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 41675001) & (POS < 41700000)" > 1613.vcf
bsub.py --threads 3 -q long 4 2662 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 67775001) & (POS < 68000000)" > 2662.vcf
bsub.py --threads 3 -q long 4 3276 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 83350001) & (POS < 83375000)" > 3276.vcf
bsub.py --threads 3 -q long 4 3285 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 83575001) & (POS < 83600000)" > tv_3285.vcf
bsub.py --threads 3 -q long 4 3624 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 3750001) & (POS < 3800000)" > tv_3624.vcf
bsub.py --threads 3 -q long 4 3633 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 4050001) & (POS < 4075000)" > tv_3633.vcf
bsub.py --threads 3 -q long 4 4727 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 31850001) & (POS < 31875000)" > tv_4727.vcf
bsub.py --threads 3 -q long 4 4926 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 36900001) & (POS < 36925000)" > tv_4926.vcf
bsub.py --threads 3 -q normal 4 5139 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 42275001) & (POS < 42525000)" > tv_5139.vcf
bsub.py --threads 3 -q normal 4 5343 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 47500001) & (POS < 47850000)" > tv_5343.vcf
bsub.py --threads 3 -q normal 4 5412 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 1450001) & (POS < 1475000)" > tv_5412.vcf
bsub.py --threads 3 -q long 4 5870 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 16325001) & (POS < 16350000)" > tv_5870.vcf
bsub.py --threads 3 -q long 4 6230 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 25425001) & (POS < 25450000)" > tv_6230.vcf
bsub.py --threads 3 -q long 4 6514 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 32700001) & (POS < 32725000)" > tv_6514.vcf
bsub.py --threads 3 -q long 4 6707 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 38025001) & (POS < 38050000)" > tv_6707.vcf
bsub.py --threads 3 -q long 4 7042 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 46600001) & (POS < 46625000)" > tv_7042.vcf
bsub.py --threads 3 -q long 4 7071 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 47450001) & (POS < 47475000)" > tv_7071.vcf
bsub.py --threads 3 -q long 4 7140 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 49275001) & (POS < 49300000)" > tv_7140.vcf
bsub.py --threads 3 -q long 4 7186 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 50425001) & (POS < 50450000)" > tv_7186.vcf
bsub.py --threads 3 -q long 4 7435 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 7050001) & (POS < 7075000)" > tv_7435.vcf
bsub.py --threads 3 -q long 4 7808 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 16550001) & (POS < 16600000)" > tv_7808.vcf
bsub.py --threads 3 -q long 4 8104 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 24025001) & (POS < 24125000)" > tv_8104.vcf
bsub.py --threads 3 -q long 4 8270 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 28200001) & (POS < 28275000)" > tv_8270.vcf
bsub.py --threads 3 -q long 4 8973 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 46125001) & (POS < 46150000)" > tv_8973.vcf
bsub.py --threads 3 -q long 4 9067 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 575001) & (POS < 2950000)" > tv_9067.vcf
bsub.py --threads 3 -q long 4 9489 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 14750001) & (POS < 14775000)" > tv_9489.vcf
bsub.py --threads 3 -q long 4 9527 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 15750001) & (POS < 15775000)" > tv_9527.vcf
bsub.py --threads 3 -q long 4 9724 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 21000001) & (POS < 21025000)" > tv_9724.vcf
bsub.py --threads 3 -q long 4 9777 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 22450001) & (POS < 22475000)" > tv_9777.vcf
bsub.py --threads 3 -q long 4 9830 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 23800001) & (POS < 23825000)" > tv_9830.vcf
bsub.py --threads 3 -q long 4 9910 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_6')" | java -jar SnpSift.jar filter "(POS > 700001) & (POS < 725000)" > tv_9910.vcf
bsub.py --threads 3 -q long 4 10154 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_6')" | java -jar SnpSift.jar filter "(POS > 6825001) & (POS < 6850000)" > tv_10154.vcf
bsub.py --threads 3 -q long 4 10187 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_6')" | java -jar SnpSift.jar filter "(POS > 7800001) & (POS < 7825000)" > tv_10187.vcf
bsub.py --threads 3 -q long 4 10269 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_6')" | java -jar SnpSift.jar filter "(POS > 9825001) & (POS < 9875000)" > tv_10269.vcf
bsub.py --threads 3 -q long 4 10927 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_7')" | java -jar SnpSift.jar filter "(POS > 1625001) & (POS < 1650000)" > tv_10927.vcf
bsub.py --threads 3 -q long 4 11127 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_7')" | java -jar SnpSift.jar filter "(POS > 6800001) & (POS < 6825000)" > tv_11127.vcf
bsub.py --threads 3 -q long 4 11229 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_7')" | java -jar SnpSift.jar filter "(POS > 9425001) & (POS < 9450000)" > tv_11229.vcf
bsub.py --threads 3 -q long 4 11479 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_7')" | java -jar SnpSift.jar filter "(POS > 15050001) & (POS < 15900000)" > tv_11479.vcf
bsub.py --threads 3 -q long 4 11702 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 2375001) & (POS < 2400000)" > tv_11702.vcf
bsub.py --threads 3 -q long 4 11734 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 3125001) & (POS < 3200000)" > tv_11734.vcf
bsub.py --threads 3 -q long 4 11933 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 8325001) & (POS < 8350000)" > tv_11933.vcf
bsub.py --threads 3 -q long 4 12051 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 11050001) & (POS < 11375000)" > tv_12051.vcf
bsub.py --threads 3 -q long 4 12401 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 20175001) & (POS < 20225000)" > tv_12401.vcf
bsub.py --threads 3 -q long 4 12704 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 27025001) & (POS < 27925000)" > tv_12704.vcf
bsub.py --threads 3 -q long 4 12711 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 28075001) & (POS < 28100000)" > tv_12711.vcf
bsub.py --threads 3 -q long 4 12717 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 28225001) & (POS < 28250000)" > tv_12717.vcf
bsub.py --threads 3 -q long 4 12956 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 34350001) & (POS < 34375000)" > tv_12956.vcf
bsub.py --threads 3 -q long 4 12989 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 35175001) & (POS < 35200000)" > tv_12989.vcf
bsub.py --threads 3 -q long 4 13012 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 35750001) & (POS < 35775000)" > tv_13012.vcf
bsub.py --threads 3 -q long 4 13041 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 36550001) & (POS < 36575000)" > tv_13041.vcf
bsub.py --threads 3 -q long 4 13095 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 38125001) & (POS < 38150000)" > tv_13095.vcf
bsub.py --threads 3 -q long 4 13110 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 38500001) & (POS < 38525000)" > tv_13110.vcf
bsub.py --threads 3 -q long 4 13213 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 41025001) & (POS < 41175000)" > tv_13213.vcf
bsub.py --threads 3 -q long 4 13273 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 42650001) & (POS < 42675000)" > tv_13273.vcf
bsub.py --threads 3 -q long 4 13855 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 57425001) & (POS < 57450000)" > tv_13855.vcf
bsub.py --threads 3 -q long 4 13966 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 60275001) & (POS < 60300000)" > tv_13966.vcf
bsub.py --threads 3 -q long 4 14051 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 62425001) & (POS < 62450000)" > tv_14051.vcf
bsub.py --threads 3 -q long 4 14183 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 65725001) & (POS < 65750000)" > tv_14183.vcf
bsub.py --threads 3 -q long 4 14963 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 85475001) & (POS < 85500000)" > tv_14963.vcf

# Pre.post#
bsub.py --threads 3 -q long 4 138 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 3675001) & (POS < 3700000)" > tv_138.vcf
bsub.py --threads 3 -q long 4 553 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 14700001) & (POS < 14725000)" > tv_553.vcf
bsub.py --threads 3 -q long 4 1142 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 29700001) & (POS < 29725000)" > tv_1142.vcf
bsub.py --threads 3 -q long 4 1395 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 36100001) & (POS < 36125000)" > tv_1395.vcf
bsub.py --threads 3 -q long 4 1702 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 43900001) & (POS < 43925000)" > tv_1702.vcf
bsub.py --threads 3 -q long 4 1742 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 44900001) & (POS < 44925000)" > tv_1742.vcf
bsub.py --threads 3 -q long 4 2163 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 55500001) & (POS < 55525000)" > tv_2163.vcf
bsub.py --threads 3 -q long 4 2369 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 60625001) & (POS < 60675000)" > tv_2369.vcf
bsub.py --threads 3 -q long 4 2878 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 73375001) & (POS < 73400000)" > tv_2878.vcf
bsub.py --threads 3 -q long 4 3113 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_1')" | java -jar SnpSift.jar filter "(POS > 79275001) & (POS < 79300000)" > tv_3113.vcf
bsub.py --threads 3 -q long 4 3612 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 3450001) & (POS < 3500000)" > tv_3612.vcf
bsub.py --threads 3 -q long 4 3966 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 12475001) & (POS < 12500000)" > tv_3966.vcf
bsub.py --threads 3 -q long 4 4177 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 17775001) & (POS < 17850000)" > tv_4177.vcf
bsub.py --threads 3 -q long 4 4732 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 31675001) & (POS < 32000000)" > tv_4732.vcf
bsub.py --threads 3 -q long 4 4925 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 36875001) & (POS < 36900000)" > tv_4925.vcf
bsub.py --threads 3 -q long 4 5194 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_2')" | java -jar SnpSift.jar filter "(POS > 43950001) & (POS < 43975000)" > tv_5194.vcf
bsub.py --threads 3 -q long 4 5870 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 16325001) & (POS < 16350000)" > tv_5870.vcf
bsub.py --threads 3 -q long 4 6403 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 29825001) & (POS < 29850000)" > tv_6403.vcf
bsub.py --threads 3 -q long 4 6836 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 41250001) & (POS < 41275000)" > tv_6836.vcf
bsub.py --threads 3 -q long 4 7047 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_3')" | java -jar SnpSift.jar filter "(POS > 46850001) & (POS < 46875000)" > tv_7047.vcf
bsub.py --threads 3 -q long 4 7312 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 3275001) & (POS < 3300000)" > tv_7312.vcf
bsub.py --threads 3 -q long 4 7319 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 3550001) & (POS < 3575000)" > tv_7319.vcf
bsub.py --threads 3 -q long 4 7734 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 14725001) & (POS < 14750000)" > tv_7734.vcf
bsub.py --threads 3 -q normal 4 7903 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 18975001) & (POS < 19000000)" > tv_7903.vcf
bsub.py --threads 3 -q long 4 7931 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 19725001) & (POS < 19750000)" > tv_7931.vcf
bsub.py --threads 3 -q long 4 8293 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 28875001) & (POS < 28900000)" > tv_8293.vcf
bsub.py --threads 3 -q long 4 8421 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_4')" | java -jar SnpSift.jar filter "(POS > 32150001) & (POS < 32175000)" > tv_8421.vcf
bsub.py --threads 3 -q long 4 9037 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 675001) & (POS < 700000)" > tv_9037.vcf
bsub.py --threads 3 -q long 4 9044 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 1250001) & (POS < 1300000)" > tv_9044.vcf
bsub.py --threads 3 -q long 4 9067 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 2925001) & (POS < 2950000)" > tv_9067.vcf
bsub.py --threads 3 -q long 4 9136 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 5200001) & (POS < 5225000)" > tv_9136.vcf
bsub.py --threads 3 -q long 4 9556 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 16625001) & (POS < 16650000)" > tv_9556.vcf
bsub.py --threads 3 -q long 4 9651 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 19000001) & (POS < 19025000)" > tv_9651.vcf
bsub.py --threads 3 -q long 4 10093 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_6')" | java -jar SnpSift.jar filter "(POS > 5300001) & (POS < 5325000)" > tv_10093.vcf
bsub.py --threads 3 -q long 4 10867 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_7')" | java -jar SnpSift.jar filter "(POS > 100001) & (POS < 125000)" > tv_10867.vcf
bsub.py --threads 3 -q long 4 11126 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_7')" | java -jar SnpSift.jar filter "(POS > 6750001) & (POS < 6775000)" > tv_11126.vcf
bsub.py --threads 3 -q long 4 11461 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_7')" | java -jar SnpSift.jar filter "(POS > 15400001) & (POS < 15425000)" > tv_11461.vcf
bsub.py --threads 3 -q long 4 11621 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 350001) & (POS < 375000)" > tv_11621.vcf
bsub.py --threads 3 -q long 4 11675 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 1700001) & (POS < 1725000)" > tv_11675.vcf
bsub.py --threads 3 -q long 4 11933 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 8325001) & (POS < 8350000)" > tv_11933.vcf
bsub.py --threads 3 -q normal 4 12051 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 11200001) & (POS < 11375000)" > tv_12051.vcf
bsub.py --threads 3 -q long 4 12144 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 13775001) & (POS < 13800000)" > tv_12144.vcf
bsub.py --threads 3 -q long 4 12205 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 15250001) & (POS < 15325000)" > tv_12205.vcf
bsub.py --threads 3 -q long 4 12237 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 15850001) & (POS < 16125000)" > tv_12237.vcf
bsub.py --threads 3 -q long 4 12405 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 20150001) & (POS < 20325000)" > tv_12405.vcf
bsub.py --threads 3 -q long 4 12455 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 21550001) & (POS < 21575000)" > tv_12455.vcf
bsub.py --threads 3 -q long 4 12613 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 25500001) & (POS < 25525000)" > tv_12613.vcf
bsub.py --threads 3 -q long 4 12647 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 26325001) & (POS < 26400000)" > tv_12647.vcf
bsub.py --threads 3 -q long 4 12713 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 28075001) & (POS < 28150000)" > tv_12713.vcf
bsub.py --threads 3 -q long 4 12726 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 28450001) & (POS < 28475000)" > tv_12726.vcf
bsub.py --threads 3 -q long 4 12734 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 28650001) & (POS < 28725000)" > tv_12734.vcf
bsub.py --threads 3 -q long 4 12779 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 29800001) & (POS < 29850000)" > tv_12779.vcf
bsub.py --threads 3 -q long 4 12999 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 35425001) & (POS < 35450000)" > tv_12999.vcf
bsub.py --threads 3 -q long 4 13006 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 35600001) & (POS < 35625000)" > tv_13006.vcf
bsub.py --threads 3 -q long 4 13015 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 35750001) & (POS < 35900000)" > tv_13015.vcf
bsub.py --threads 3 -q long 4 13087 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 37925001) & (POS < 37950000)" > tv_13087.vcf
bsub.py --threads 3 -q long 4 13091 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 38025001) & (POS < 38050000)" > tv_13091.vcf
bsub.py --threads 3 -q long 4 13097 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 38175001) & (POS < 38200000)" > tv_13097.vcf
bsub.py --threads 3 -q long 4 13115 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 38625001) & (POS < 38650000)" > tv_13115.vcf
bsub.py --threads 3 -q long 4 13127 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 38925001) & (POS < 38950000)" > tv_13127.vcf
bsub.py --threads 3 -q long 4 13804 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 56050001) & (POS < 56100000)" > tv_13804.vcf
bsub.py --threads 3 -q long 4 14183 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 65725001) & (POS < 65750000)" > tv_14183.vcf
bsub.py --threads 3 -q long 4 14226 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 66775001) & (POS < 66825000)" > tv_14226.vcf
bsub.py --threads 3 -q long 4 14286 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 68250001) & (POS < 68325000)" > tv_14286.vcf
bsub.py --threads 3 -q long 4 14708 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 78975001) & (POS < 79000000)" > tv_14708.vcf
bsub.py --threads 3 -q long 4 14744 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 79875001) & (POS < 79900000)" > tv_14744.vcf
bsub.py --threads 3 -q long 4 14965 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 85525001) & (POS < 85550000)" > tv_14965.vcf
bsub.py --threads 3 -q long 4 15026 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 87050001) & (POS < 87150000)" > tv_15026.vcf

bsub.py --threads 3 -q long 4 fst5 cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_5')" | java -jar SnpSift.jar filter "(POS > 7780001) & (POS < 8990000)" > fst5.vcf
bsub.py --threads 3 -q long 4 fstzw cat 174_new.ann.vcf | java -jar SnpSift.jar filter "(CHROM = 'SM_V7_ZW')" | java -jar SnpSift.jar filter "(POS > 12620001) & (POS < 12780000)" > fstzw.vcf

# Regions under selection tp1.tp2#
#extracting genes std.int#
bsub.py --threads 3 -q normal 4 r81 ./genes4.sh
java -jar SnpSift.jar extractFields TV9.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > tv9_genes.txt
java -jar SnpSift.jar extractFields tv_148.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > genes_148.txt
java -jar SnpSift.jar extractFields TV_745_746.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > genes_746.txt
java -jar SnpSift.jar extractFields tv_11479.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > tv_479.txt

#Pre.post#
java -jar SnpSift.jar extractFields chr4_region35.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > region35.txt
java -jar SnpSift.jar extractFields chr1_region12.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > region12.txt
java -jar SnpSift.jar extractFields chr1_region9.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > region9.txt
java -jar SnpSift.jar extractFields chr1_region5.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > region5.txt
java -jar SnpSift.jar extractFields chr1_region6.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > region6.txt
java -jar SnpSift.jar extractFields Chr6_region47.vcf CHROM POS ID AF "ANN[*].IMPACT" "ANN[*].GENEID" "ANN[*].EFFECT" | grep -v "intergenic" > region47.txt

#extracting geneIDs std.int#
java -jar SnpSift.jar extractFields TV9.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv9_geneIDs.txt
java -jar SnpSift.jar extractFields tv_148.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > 148_geneIDs.txt
java -jar SnpSift.jar extractFields TV_745_746.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > 746_IDs.txt
java -jar SnpSift.jar extractFields 1037.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > 1037.txt
java -jar SnpSift.jar extractFields tv_1080.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_1080.txt
java -jar SnpSift.jar extractFields tv_1214.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv1214_ID.txt
java -jar SnpSift.jar extractFields 1414.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > 1414_ID.txt
java -jar SnpSift.jar extractFields 1613.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > 1613_ID.txt
java -jar SnpSift.jar extractFields 2662.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > 2662_ID.txt
java -jar SnpSift.jar extractFields 3276.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > 3276_ID.txt
java -jar SnpSift.jar extractFields tv_3285.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_3285_ID.txt
java -jar SnpSift.jar extractFields tv_3624.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_3624_ID.txt
java -jar SnpSift.jar extractFields tv_3633.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_3633.txt
java -jar SnpSift.jar extractFields tv_4727.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_4727_id.txt
java -jar SnpSift.jar extractFields tv_4926.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_4926_id.txt
java -jar SnpSift.jar extractFields tv_5139.vcf  CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_5139_id.txt
java -jar SnpSift.jar extractFields tv_5343.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_5343.txt
java -jar SnpSift.jar extractFields tv_5412.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_5412.txt
java -jar SnpSift.jar extractFields tv_5870.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_5870_id.txt
java -jar SnpSift.jar extractFields tv_6230.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_6230_id.txt
java -jar SnpSift.jar extractFields tv_6514.vcf  CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_6514_id.txt
java -jar SnpSift.jar extractFields tv_6707.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_6707_id.txt
java -jar SnpSift.jar extractFields tv_7042.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7042_id.txt
java -jar SnpSift.jar extractFields tv_7071.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7071_id.txt
java -jar SnpSift.jar extractFields tv_7140.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7140_id.txt
java -jar SnpSift.jar extractFields tv_7186.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7186_id.txt
java -jar SnpSift.jar extractFields tv_7435.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7435_id.txt
java -jar SnpSift.jar extractFields tv_7808.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7808_id.txt
java -jar SnpSift.jar extractFields tv_8104.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_8104_id.txt
java -jar SnpSift.jar extractFields tv_8270.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_8270_id.txt
java -jar SnpSift.jar extractFields tv_8973.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_8973_id.txt
java -jar SnpSift.jar extractFields tv_9067.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9067_id.txt
java -jar SnpSift.jar extractFields tv_9489.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9489_id.txt
java -jar SnpSift.jar extractFields tv_9527.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9527_id.txt
java -jar SnpSift.jar extractFields tv_9724.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9724_id.txt
java -jar SnpSift.jar extractFields tv_9777.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9777_id.txt
java -jar SnpSift.jar extractFields tv_9830.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9830_id.txt
java -jar SnpSift.jar extractFields tv_9910.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9910_id.txt
java -jar SnpSift.jar extractFields tv_10154.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_10154_id.txt
java -jar SnpSift.jar extractFields tv_10187.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_10187_id.txt
java -jar SnpSift.jar extractFields tv_10927.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_10927_id.txt
java -jar SnpSift.jar extractFields tv_11127.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11127_id.txt
java -jar SnpSift.jar extractFields tv_11229.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11229_id.txt
java -jar SnpSift.jar extractFields tv_11479.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11479_id.txt
java -jar SnpSift.jar extractFields tv_11702.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11702_id.txt
java -jar SnpSift.jar extractFields tv_11933.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11933_id.txt
java -jar SnpSift.jar extractFields tv_12051.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12051_id.txt
java -jar SnpSift.jar extractFields tv_12401.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12401_id.txt
java -jar SnpSift.jar extractFields tv_12704.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12704_id.txt
java -jar SnpSift.jar extractFields tv_12711.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12711_id.txt
java -jar SnpSift.jar extractFields tv_12717.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12717_id.txt
java -jar SnpSift.jar extractFields tv_12956.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12956_id.txt
java -jar SnpSift.jar extractFields tv_12989.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12989_id.txt
java -jar SnpSift.jar extractFields tv_13012.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13012_id.txt
java -jar SnpSift.jar extractFields tv_13095.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13095_id.txt
java -jar SnpSift.jar extractFields tv_13110.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13110_id.txt
java -jar SnpSift.jar extractFields tv_13213.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13213_id.txt
java -jar SnpSift.jar extractFields tv_13273.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13273_id.txt
java -jar SnpSift.jar extractFields tv_13855.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13855_id.txt
java -jar SnpSift.jar extractFields tv_13966.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13966_id.txt
java -jar SnpSift.jar extractFields tv_14051.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_14051_id.txt
java -jar SnpSift.jar extractFields tv_14183.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_14183_id.txt
java -jar SnpSift.jar extractFields tv_14963.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_14963_id.txt

#Pre.post#
java -jar SnpSift.jar extractFields tv_138.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_138_id.txt
java -jar SnpSift.jar extractFields tv_553.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_553_id.txt
java -jar SnpSift.jar extractFields tv_1142.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_1142_id.txt
java -jar SnpSift.jar extractFields tv_1395.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_1395_id.txt
java -jar SnpSift.jar extractFields tv_1702.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_1702_id.txt
java -jar SnpSift.jar extractFields tv_1742.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_1742_id.txt
java -jar SnpSift.jar extractFields tv_2163.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_2163_id.txt
java -jar SnpSift.jar extractFields tv_2369.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_2369_id.txt
java -jar SnpSift.jar extractFields tv_2878.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_2878_id.txt
java -jar SnpSift.jar extractFields tv_3113.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_3113_id.txt
java -jar SnpSift.jar extractFields tv_3612.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_3612_id.txt
java -jar SnpSift.jar extractFields tv_3966.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_3966_id.txt
java -jar SnpSift.jar extractFields tv_4177.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_4177_id.txt
java -jar SnpSift.jar extractFields tv_4732.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_4732_id.txt
java -jar SnpSift.jar extractFields tv_4925.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_4925_id.txt
java -jar SnpSift.jar extractFields tv_5194.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_5194_id.txt
java -jar SnpSift.jar extractFields tv_5870.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_5870_id.txt
java -jar SnpSift.jar extractFields tv_6403.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_6403_id.txt
java -jar SnpSift.jar extractFields tv_6836.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_6836_id.txt
java -jar SnpSift.jar extractFields tv_7047.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7047_id.txt
java -jar SnpSift.jar extractFields tv_7312.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7312_id.txt
java -jar SnpSift.jar extractFields tv_7319.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7319_id.txt
java -jar SnpSift.jar extractFields tv_7734.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7734_id.txt
java -jar SnpSift.jar extractFields tv_7903.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7903_id.txt
java -jar SnpSift.jar extractFields tv_7931.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_7931_id.txt
java -jar SnpSift.jar extractFields tv_8293.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_8293_id.txt
java -jar SnpSift.jar extractFields tv_8421.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_8421_id.txt
java -jar SnpSift.jar extractFields tv_9037.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9037_id.txt
java -jar SnpSift.jar extractFields tv_9044.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9044_id.txt
java -jar SnpSift.jar extractFields tv_9067.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9067_id.txt
java -jar SnpSift.jar extractFields tv_9136.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9136_id.txt
java -jar SnpSift.jar extractFields tv_9556.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9556_id.txt
java -jar SnpSift.jar extractFields tv_9651.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_9651_id.txt
java -jar SnpSift.jar extractFields tv_10093.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_10093_id.txt
java -jar SnpSift.jar extractFields tv_10867.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_10867_id.txt
java -jar SnpSift.jar extractFields tv_11126.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11126_id.txt
java -jar SnpSift.jar extractFields tv_11461.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11461_id.txt
java -jar SnpSift.jar extractFields tv_11621.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11621_id.txt
java -jar SnpSift.jar extractFields tv_11675.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11675_id.txt
java -jar SnpSift.jar extractFields tv_11933.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_11933_id.txt
java -jar SnpSift.jar extractFields tv_12051.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12051_id.txt
java -jar SnpSift.jar extractFields tv_12144.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12144_id.txt
java -jar SnpSift.jar extractFields tv_12205.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12205_id.txt
java -jar SnpSift.jar extractFields tv_12237.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12237_id.txt
java -jar SnpSift.jar extractFields tv_12405.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12405_id.txt
java -jar SnpSift.jar extractFields tv_12455.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12455_id.txt
java -jar SnpSift.jar extractFields tv_12613.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12613_id.txt
java -jar SnpSift.jar extractFields tv_12647.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12647_id.txt
java -jar SnpSift.jar extractFields tv_12713.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12713_id.txt
java -jar SnpSift.jar extractFields tv_12726.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12726_id.txt
java -jar SnpSift.jar extractFields tv_12734.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12734_id.txt
java -jar SnpSift.jar extractFields tv_12779.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12779_id.txt
java -jar SnpSift.jar extractFields tv_12999.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_12999_id.txt
java -jar SnpSift.jar extractFields tv_13006.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13006_id.txt
java -jar SnpSift.jar extractFields tv_13015.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13015_id.txt
java -jar SnpSift.jar extractFields tv_13087.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13087_id.txt
java -jar SnpSift.jar extractFields tv_13091.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13091_id.txt
java -jar SnpSift.jar extractFields tv_13097.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13097_id.txt
java -jar SnpSift.jar extractFields tv_13115.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13115_id.txt
java -jar SnpSift.jar extractFields tv_13127.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13127_id.txt
java -jar SnpSift.jar extractFields tv_13804.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_13804_id.txt
java -jar SnpSift.jar extractFields tv_14183.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_14183_id.txt
java -jar SnpSift.jar extractFields tv_14286.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_14286_id.txt
java -jar SnpSift.jar extractFields tv_14708.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_14708_id.txt
java -jar SnpSift.jar extractFields tv_14744.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_14744_id.txt
java -jar SnpSift.jar extractFields tv_14965.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_14965_id.txt
java -jar SnpSift.jar extractFields tv_15026.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > tv_15026_id.txt

java -jar SnpSift.jar extractFields fst5.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > fst5_id.txt
java -jar SnpSift.jar extractFields fstzw.vcf CHROM POS ID AF "ANN[*].GENEID" "ANN[*].EFFECT" "ANN[*].IMPACT" | grep -v "intergenic" | cut -f5 | sort | uniq > fstzw_id.txt

#Picking regions of interest std.int#
cd /nfs/repository/working_area/SHISTO/V7/Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_1" && $3=="mRNA" && $4 >19550001 && $4 < 19600000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_1"  && $3=="mRNA" && $4 >27025001 && $4 < 27050000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_1"  && $3=="mRNA" && $4 >41675001 && $4 < 41700000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_1" && $3=="mRNA" && $4 >83350001 && $4 < 83375000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_2" && $3=="mRNA" && $4 >3750001 && $4 < 3800000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_3" && $3=="mRNA" && $4 >1450001 && $4 < 1475000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_3" && $3=="mRNA" && $4 >16325001 && $4 < 16350000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_3" && $3=="mRNA" && $4 >25425001 && $4 < 25450000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_3" && $3=="mRNA" && $4 >38025001 && $4 < 38050000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_3" && $3=="mRNA" && $4 >47450001 && $4 < 47475000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_3" && $3=="mRNA" && $4 >49275001 && $4 < 49300000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_3" && $3=="mRNA" && $4 >31500001 && $4 < 31525000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_4" && $3=="mRNA" && $4 >16550001 && $4 < 16600000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >575001 && $4 < 2950000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >14750001 && $4 < 14775000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >21000001 && $4 < 21025000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >23800001 && $4 < 23825000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_6" && $3=="mRNA" && $4 >6825001 && $4 < 6850000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_6" && $3=="mRNA" && $4 >7800001 && $4 < 7825000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_6" && $3=="mRNA" && $4 >29700001 && $4 < 29725000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_6" && $3=="mRNA" && $4 >9825001 && $4 < 9875000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_7" && $3=="mRNA" && $4 >9425001 && $4 < 9450000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_7" && $3=="mRNA" && $4 >15050001 && $4 < 15900000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >3125001 && $4 < 3200000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >8325001 && $4 < 8350000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >27025001 && $4 < 27925000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >28075001 && $4 < 28100000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >28225001 && $4 < 28250000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >34350001 && $4 < 34375000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >35750001 && $4 < 35775000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >36900001 && $4 < 36925000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >42650001 && $4 < 42675000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >57425001 && $4 < 57450000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 > 65725001 && $4 < 65750000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >85475001 && $4 < 85500000 {print$9}' Sm_v7.2_all-validated.gff

# Pre.post #
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >350001 && $4 < 375000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_1" && $3=="mRNA" && $4 >29700001 && $4 < 29725000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_1" && $3=="mRNA" && $4 >55500001 && $4 < 55525000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_1" && $3=="mRNA" && $4 >60625001 && $4 < 60675000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_1" && $3=="mRNA" && $4 >73375001 && $4 < 73400000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_1" && $3=="mRNA" && $4 >79275001 && $4 < 79300000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_2" && $3=="mRNA" && $4 >3450001 && $4 < 32725000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_2" && $3=="mRNA" && $4 >12475001 && $4 < 12500000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_2" && $3=="mRNA" && $4 >31675001 && $4 < 32000000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_2" && $3=="mRNA" && $4 >36875001 && $4 < 36900000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_2" && $3=="mRNA" && $4 >43950001 && $4 < 43975000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_3" && $3=="mRNA" && $4 >16325001 && $4 < 16350000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_3" && $3=="mRNA" && $4 >29825001 && $4 < 29850000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_4" && $3=="mRNA" && $4 >14725001 && $4 < 14750000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_4" && $3=="mRNA" && $4 >19725001 && $4 < 19750000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_4" && $3=="mRNA" && $4 >32150001 && $4 < 32175000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >675001 && $4 < 700000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >16625001 && $4 < 16650000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >19000001 && $4 < 19025000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_7" && $3=="mRNA" && $4 >6750001 && $4 < 6775000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_7" && $3=="mRNA" && $4 >15400001 && $4 < 15425000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >11200001 && $4 < 11375000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >13775001 && $4 < 13800000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >15250001 && $4 < 15325000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >25500001 && $4 < 25525000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >26375001 && $4 < 26400000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >28075001 && $4 < 28150000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >35750001 && $4 < 35900000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >37925001 && $4 < 37950000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >38025001 && $4 < 38050000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >38175001 && $4 < 38200000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >38625001 && $4 < 38650000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >38925001 && $4 < 38950000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >56050001 && $4 < 56100000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >65725001 && $4 < 65750000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >68250001 && $4 < 68275000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >78975001 && $4 < 79000000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >85525001 && $4 < 85550000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >87050001 && $4 < 87150000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >7780001 && $4 < 8990000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >12620001 && $4 < 12780000 {print$9}' Sm_v7.2_all-validated.gff


# Post-treatment std.int
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >8675001 && $4 < 10575000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_5" && $3=="mRNA" && $4 >8675001 && $4 < 8850000 {print$9}' Sm_v7.2_all-validated.gff

awk -F "\t" '$1=="SM_V7_6" && $3=="mRNA" && $4 >6700001 && $4 < 7550000 {print$9}' Sm_v7.2_all-validated.gff

awk -F "\t" '$1=="SM_V7_7" && $3=="mRNA" && $4 >15850001 && $4 < 15900000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_7" && $3=="mRNA" && $4 >6750001 && $4 < 6775000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_7" && $3=="mRNA" && $4 >15400001 && $4 < 15425000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >15575000 && $4 < 15575000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >2375001 && $4 < 2425000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >3125001 && $4 < 3200000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >8325001 && $4 < 8350000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >11000001 && $4 < 11375000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >20175001 && $4 < 20225000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >27025001 && $4 < 27925000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >28075001 && $4 < 28100000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >34350001 && $4 < 42675000 {print$9}' Sm_v7.2_all-validated.gff #
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >51425001 && $4 < 51450000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >57425001 && $4 < 57450000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >60275001 && $4 < 60300000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >62425001 && $4 < 62450000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >65725001 && $4 < 65775000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >85475001 && $4 < 85625000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >500001 && $4 < 525000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >1700001 && $4 < 1725000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >11200001 && $4 < 16125000 {print$9}' Sm_v7.2_all-validated.gff #
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >20125001 && $4 < 20325000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >87075001 && $4 < 87150000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >79875001 && $4 < 79900000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >78975001 && $4 < 79000000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >68250001 && $4 < 68325000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >65725001 && $4 < 65750000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >39800001 && $4 < 39825000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >35425001 && $4 < 38650000 {print$9}' Sm_v7.2_all-validated.gff #
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >29800001 && $4 < 29850000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >34350001 && $4 < 34475000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >35175001 && $4 < 35200000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >35750001 && $4 < 35775000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >36550001 && $4 < 36575000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >38125001 && $4 < 38150000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >38625001 && $4 < 38650000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >41025001 && $4 < 41175000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >42650001 && $4 < 42675000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >11200001 && $4 < 11375000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >13750001 && $4 < 13800000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >15250001 && $4 < 16125000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >20150001 && $4 < 20175000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >21550001 && $4 < 21575000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >25500001 && $4 < 25525000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >26325001 && $4 < 26400000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >28075001 && $4 < 28725000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >35425001 && $4 < 35900000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >37925001 && $4 < 37950000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >38025001 && $4 < 38050000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >38175001 && $4 < 38200000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >38625001 && $4 < 38650000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >6825001 && $4 < 6850000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >9825001 && $4 < 9875000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_2" && $3=="mRNA" && $4 >41625000 && $4 < 41650000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >350000 && $4 < 375000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >35175001 && $4 < 35200000 {print$9}' Sm_v7.2_all-validated.gff
awk -F "\t" '$1=="SM_V7_ZW" && $3=="mRNA" && $4 >35175001 && $4 < 35200000 {print$9}' Sm_v7.2_all-validated.gff

grep "SM_V7_2" Sm_v7.2_all-validated.gff | grep "mrna" -i | less
grep "SM_V7_2" Sm_v7.2_all-validated.gff | grep "mrna" -i | wc -l
grep "SM_V7_2" Sm_v7.2_Basic.gff | grep "mrna" -i | less

less Sm_v7.2_all-validated.gff | grep "mrna" -i | awk -F "\t" '$1=="SM_V7_2" && $3=="mRNA" && $4 >41000000 && $4 < 43500000' | cut -f2 -d "=" | cut -f1 -d ";" | cut -f1 -d "." | sort | uniq | less
less Sm_v7.2_all-validated.gff | grep "mrna" -i | awk -F "\t" '$1=="SM_V7_2" && $3=="mRNA" && $4 >41000000 && $4 < 43500000' | cut -f2 -d "=" | cut -f1 -d ";" | sort | uniq

#subsetting vcf#

bsub.py --threads 3 -q long 5 pre.std ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Pre_std.txt --out pre_std
bsub.py --threads 3 -q long 5 pre.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Pre_int.txt --out pre_int
bsub.py --threads 3 -q long 5 post.std ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std.txt --out post_std
bsub.py --threads 3 -q long 5 post.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int.txt --out post_int
bsub.py --threads 3 -q long 5 std ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Standard.txt --out Std
bsub.py --threads 3 -q long 5 Int ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Intensive.txt --out Int
bsub.py --threads 3 -q long 5 tp1 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Tp1.txt --out tp1
bsub.py --threads 3 -q long 5 tp2 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Tp2.txt --out tp2

bsub.py --threads 3 -q long 5 pre51 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Pre_51.txt --out pre_51
bsub.py --threads 3 -q long 5 post51 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_51.txt --out post_51
bsub.py --threads 3 -q long 5 pre_std51 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Pre_std_51.txt --out pre.std_51
bsub.py --threads 3 -q long 5 pre_int51 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Pre_int_51.txt --out pre.int_51
bsub.py --threads 3 -q long 5 post_std51 ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_std_51.txt --out post.std_51
bsub.py --threads 3 -q long 5 post_int ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --recode --recode-INFO-all --keep Sample.lists/Post_int_51.txt --out post.int_51

bsub.py --threads 3 -q long 9 pre51 ~jc17/software/vcftools_0.1.15/vcftools --vcf pre_51.recode.vcf --window-pi 10000 --out pre51_10kb
bsub.py --threads 3 -q long 9 post51 ~jc17/software/vcftools_0.1.15/vcftools --vcf post_51.recode.vcf --window-pi 10000 --out post51_10kb
bsub.py --threads 3 -q long 9 pre.std51 ~jc17/software/vcftools_0.1.15/vcftools --vcf pre.std_51.recode.vcf --window-pi 10000 --out pre.std51_10kb
bsub.py --threads 3 -q long 9 pre.int51 ~jc17/software/vcftools_0.1.15/vcftools --vcf pre.int_51.recode.vcf --window-pi 10000 --out pre.int51_10kb
bsub.py --threads 3 -q long 9 post_std51 ~jc17/software/vcftools_0.1.15/vcftools --vcf post.std_51.recode.vcf --window-pi 10000 --out post.std51_10kb
bsub.py --threads 3 -q long 9 post_int51 ~jc17/software/vcftools_0.1.15/vcftools --vcf post.int_51.recode.vcf --window-pi 10000 --out post.int51_10kb

bsub.py --threads 3 -q long 15 nd_pre ~jc17/software/vcftools_0.1.15/vcftools --vcf tp1.recode.vcf --window-pi 10000 --out pre
bsub.py --threads 3 -q long 15 nd_post ~jc17/software/vcftools_0.1.15/vcftools --vcf tp2.recode.vcf --window-pi 10000 --out post

bsup.py --threads 3 -q long 15 lugumba ~jc17/software/vcftools_0.1.15/vcftools --vcf Biallelic_SNPs_174.recode.vcf --recode --recode-INFO-all --keep List_Lugumba.txt --out Lugumba
bsup.py --threads 3 -q long 15 zingoola ~jc17/software/vcftools_0.1.15/vcftools --vcf Biallelic_SNPs_174.recode.vcf --recode --recode-INFO-all --keep List_Zingoola.txt --out Zingoola
bsup.py --threads 3 -q long 15 kitosi ~jc17/software/vcftools_0.1.15/vcftools --vcf Biallelic_SNPs_174.recode.vcf --recode --recode-INFO-all --keep List_Kitosi.txt --out Kitosi
bsup.py --threads 3 -q long 15 kisu ~jc17/software/vcftools_0.1.15/vcftools --vcf Biallelic_SNPs_174.recode.vcf --recode --recode-INFO-all --keep List_Kisu.txt --out Kisu
bsup.py --threads 3 -q long 15 katooke ~jc17/software/vcftools_0.1.15/vcftools --vcf Biallelic_SNPs_174.recode.vcf --recode --recode-INFO-all --keep List_Katooke.txt --out Katooke
bsup.py --threads 3 -q long 15 kakeeka ~jc17/software/vcftools_0.1.15/vcftools --vcf Biallelic_SNPs_174.recode.vcf --recode --recode-INFO-all --keep List_Kakeeka.txt --out Kakeeka
bsup.py --threads 3 -q long 15 kachanga ~jc17/software/vcftools_0.1.15/vcftools --vcf Biallelic_SNPs_174.recode.vcf --recode --recode-INFO-all --keep List_Kachanga.txt --out Kachanga
bsup.py --threads 3 -q long 15 busi ~jc17/software/vcftools_0.1.15/vcftools --vcf Biallelic_SNPs_174.recode.vcf --recode --recode-INFO-all --keep List_Busi.txt --out Busi

bsub.py --threads 3 -q long 15 lugumba ~jc17/software/vcftools_0.1.15/vcftools --vcf Lugumba.recode.vcf --site-pi --out Lugumba
bsub.py --threads 3 -q long 15 katooke ~jc17/software/vcftools_0.1.15/vcftools --vcf Katooke.recode.vcf --site-pi --out Katooke
bsub.py --threads 3 -q long 15 kitosi ~jc17/software/vcftools_0.1.15/vcftools --vcf Kitosi.recode.vcf --site-pi --out Kitosi
bsub.py --threads 3 -q long 15 kachanga ~jc17/software/vcftools_0.1.15/vcftools --vcf Kachanga.recode.vcf --site-pi --out Kachanga
bsub.py --threads 3 -q long 15 kisu ~jc17/software/vcftools_0.1.15/vcftools --vcf Kisu.recode.vcf --site-pi --out Kisu
bsub.py --threads 3 -q long 15 kakeeka ~jc17/software/vcftools_0.1.15/vcftools --vcf Kakeeka.recode.vcf --site-pi --out Kakeeka
bsub.py --threads 3 -q long 15 busi ~jc17/software/vcftools_0.1.15/vcftools --vcf Busi.recode.vcf --site-pi --out Busi
bsub.py --threads 3 -q long 15 zingoola ~jc17/software/vcftools_0.1.15/vcftools --vcf Zingoola.recode.vcf --site-pi --out Zingoola

bsub.py --threads 3 -q long 15 lugumba10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Lugumba.recode.vcf --window-pi 10000 --out Lugumba_10kb
bsub.py --threads 3 -q long 15 katooke10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Katooke.recode.vcf --window-pi 10000 --out Katooke_10kb
bsub.py --threads 3 -q long 15 kitosi10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Kitosi.recode.vcf --window-pi 10000 --out Kitosi_10kb
bsub.py --threads 3 -q long 15 kachanga10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Kachanga.recode.vcf --window-pi 10000 --out Kachanga_10kb
bsub.py --threads 3 -q long 15 kisu10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Kisu.recode.vcf --window-pi 10000 --out Kisu_10kb
bsub.py --threads 3 -q long 15 kakeeka10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Kakeeka.recode.vcf --window-pi 10000 --out Kakeeka_10kb
bsub.py --threads 3 -q long 15 busi10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Busi.recode.vcf --window-pi 10000 --out Busi_10kb
bsub.py --threads 3 -q long 15 zingoola10kb ~jc17/software/vcftools_0.1.15/vcftools --vcf Zingoola.recode.vcf --window-pi 10000 --out Zingoola_10kb

#merging nucleotide diversity files for different groups to be able to plot ND in R#
bash-3.2$ less nucleotide_int.sites.pi
bash-3.2$ awk '{print $1,$2,$3,FILENAME}' nucleotide_int.sites.pi | less
bash-3.2$ awk '{print $1,$2,$3,FILENAME}' nucleotide_int.sites.pi | grep -v "CHROM" | less
bash-3.2$ awk '{print $1,$2,$3,FILENAME}' nucleotide_int.sites.pi | grep -v "CHROM" | less
bash-3.2$ awk '{print $1,$2,$3,FILENAME}' nucleotide_int.sites.pi | grep -v "CHROM" | sed 's/.sites.pi//g' | less
bash-3.2$ awk '{print $1,$2,$3,FILENAME}' nucleotide_int.sites.pi | grep -v "CHROM" | sed 's/.sites.pi//g' | sed 's/nucleotide_//g' | less
bash-3.2$ for file in *.pi ; do awk '{print $1,$2,$3,FILENAME}' $file | grep -v "CHROM" | sed 's/.sites.pi//g' | sed 's/nucleotide_//g' > $file.done; done

cat *.done | sed 's/ / /g' > nucleotide_all_groups.pi
cat *.done > nucleotide_all_groups.pi

#checking memory usage of the computer through terminal# top# check running programs
#fst between the islands and outgrp#

bsub.py --threads 3 -q long 10 pre.post ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --weir-fst-pop Sample.lists/Pre_51.txt --weir-fst-pop Sample.lists/Post_51.txt --fst-window-size 10000 --out pre.post_10k
bsub.py --threads 3 -q long 10 pre_std.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --weir-fst-pop Sample.lists/Pre_std_51.txt --weir-fst-pop Sample.lists/Pre_int_51.txt --fst-window-size 10000 --out pre_std.int_10k
bsub.py --threads 3 -q long 10 post_std.int ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --weir-fst-pop Sample.lists/Post_std_51.txt --weir-fst-pop Sample.lists/Post_int_51.txt --fst-window-size 10000 --out post_std.int_10k

#merging all the 173 bam files#
bsub.py --threads 3 -q normal 10 173_merged bamtools merge -out 173_merged.bam
bsub.py --threads 3 -q normal 10 173_merged samtools merge 173_Merged.bam *.bam

samtools merge --bam-list Islands_IDs.txt

#viewing a bamfile#
samtools view -h 100384.pe.markdup.bam | less

#Indexing the file to use in IGV#
bgzip -c Biallelic_nohap.vcf.recode.vcf > Biallelic_nohap.vcf.recode.vcf.gz
bsub.py --threads 3 -q yesterday 10 IndexingVcf tabix -p vcf Biallelic_nohap.vcf.recode.vcf.gzpre10kb_std.int

bsub.py --threads 3 -q yesterday 10 stdzip bgzip -c Std_nohap.recode.vcf.recode.vcf > Std_nohap.recode.vcf.recode.vcf.gz
bsub.py --threads 3 -q yesterday 10 intzip bgzip -c Int_nohap.recode.vcf.recode.vcf > Int_nohap.recode.vcf.recode.vcf.gz
bsub.py --threads 3 -q yesterday 10 tp1zip bgzip -c Tp1_nohap.recode.vcf.recode.vcf > Tp1_nohap.recode.vcf.recode.vcf.gz
bsub.py --threads 3 -q yesterday 10 tp2zip bgzip -c Tp2_nohap.recode.vcf.recode.vcf > Tp2_nohap.recode.vcf.recode.vcf.gz

bsub.py --threads 3 -q yesterday 10 Indexstd tabix -p vcf Std_nohap.recode.vcf.recode.vcf.gz
bsub.py --threads 3 -q yesterday 10 Indexint tabix -p vcf Int_nohap.recode.vcf.recode.vcf.gz
bsub.py --threads 3 -q long 10 Indextp1 tabix -p vcf Tp1_nohap.recode.vcf.recode.vcf.gz
bsub.py --threads 3 -q long 10 Indextp2 tabix -p vcf Tp2_nohap.recode.vcf.recode.vcf.gz

#Extracting mapping qualities from vcf files#
bsub.py --threads 3 -q long 10 stdmq ~jc17/software/vcftools_0.1.15/vcftools --vcf Std_nohap.recode.vcf.recode.vcf --get-INFO AF --get-INFO MQ --out stdMQ
bsub.py --threads 3 -q long 10 intmq ~jc17/software/vcftools_0.1.15/vcftools --vcf Int_nohap.recode.vcf.recode.vcf --get-INFO AF --get-INFO MQ --out intMQ
bsub.py --threads 3 -q long 10 tp1mq ~jc17/software/vcftools_0.1.15/vcftools --vcf Tp1_nohap.recode.vcf.recode.vcf --get-INFO AF --get-INFO MQ --out tp1MQ
bsub.py --threads 3 -q long 10 tp2mq ~jc17/software/vcftools_0.1.15/vcftools --vcf Tp2_nohap.recode.vcf.recode.vcf --get-INFO AF --get-INFO MQ --out tp2MQ

/lustre/scratch118/infgen/pathogen/pathpipe/helminths/seq-pipelines/Schistosoma/mansoni/TRACKING/5582/5582STDY7724264/SLX/22637246/28204#33

/lustre/scratch118/infgen/team133/db22/software/bwa/bwa bwa /lustre/scratch118/infgen/team133/db22/crellen_remap/REFERENCE/Sm_v7_nohap.fa \
        5582STDY7771000 /lustre/scratch118/infgen/team133/jt24/Fastq/'28203#100'_1.fastq.gz /lustre/scratch118/infgen/team133/jt24/Fastq/'28203#100'_2.fastq.gz

--bwa_mem --samtools_path /software/pathogen/external/apps/usr/bin/samtools --keep_undupped --bwa_path /lustre/scratch118/infgen/team133/db22/software/bwa/bwa bwa /lustre/scratch118/infgen/team133/db22/crellen_remap/REFERENCE/Sm_v7_nohap.fa 5582STDY7771029 /lustre/scratch118/infgen/team133/jt24/Fastq/'28203#19'_1
#finding a work mong subdirectories
find -name "FINI*" | wc -l

grep --exclude=\*.{o} -rnw -e "Exited" ./#Variant calling failed jobs

#mapping two duplicate samples!
5582STDY7759906  28204#25_2.  28204#25_1.
5582STDY7771004  28204#60_2.  28204#60_1.

bwa mem /lustre/scratch118/infgen/team133/jt24/Fastq/MAPPED_BAMs/Variant_calling/Ref_nohap/Sm_v7_nohap.fa <in1.fq> [in2.fq]

bsub.py --threads 3 -q basement 10 map1004 ./map1.sh
--bwa_mem --samtools_path /software/pathogen/external/apps/usr/bin/samtools --keep_undupped --bwa_path /lustre/scratch118/infgen/team133/db22/software/bwa/bwa bwa /lustre/scratch118/infgen/team133/jt24/Fastq/MAPPED_BAMs/Variant_calling/Ref_nohap/Sm_v7_nohap.fa 5582STDY7771004 /lustre/scratch118/infgen/team133/jt24/Fastq/'28204#60'_1.fastq.gz /lustre/scratch118/infgen/team133/jt24/Fastq/'28204#60'_2.fastq.gz > 1004.sam

bwa mem -M -t 4 Ref_nohap/Sm_v7_nohap.fa 28204#60_1.fastq.gz 28204#60_2.fastq.gz | samtools view -b | samtools sort  > 5582STDY7771004.sam
bwa mem -M -t 4 Ref_nohap/Sm_v7_nohap.fa 28204#25_1.fastq.gz 28204#25_2.fastq.gz |  samtools view -b  samtools sort > 5582STDY7759906.sam

bsub.py --threads 4 -q long 15 04bam samtools view 5582STDY7771004.sam -b -o 5582STDY7771004_test.bam
bsub.py --threads 4 -q long 15 06bam samtools view 5582STDY7759906.sam -b -o 5582STDY7759906.bam

bsub.py --threads 4 -q long 15 04bam /nfs/users/nfs_e/ea10/downloaded_software/samtools-1.3/samtools view  5582STDY7771004.sam -b -o 5582STDY7771004.bam

bsub.py --threads 4 -q long 15 sort04 /nfs/users/nfs_e/ea10/downloaded_software/samtools-1.3/

-n 5582STDY7771004.bam -o 5582STDY7771004.SORTED.bam
bsub.py --threads 4 -q long 15 sort06 /nfs/users/nfs_e/ea10/downloaded_software/samtools-1.3/samtools sort -n 5582STDY7759906.bam -o 5582STDY7759906.SORTED.bam

bsub.py --threads 4 -q long 15 fixt04 /nfs/users/nfs_e/ea10/downloaded_software/samtools-1.3/samtools fixmate 5582STDY7771004.SORTED.bam 5582STDY7771004.fixmate.bam
bsub.py --threads 4 -q long 15 fixt04s /nfs/users/nfs_e/ea10/downloaded_software/samtools-1.3/samtools sort -o 5582STDY7771004.fixmatep.bam 5582STDY7771004.fixmate.bam

# removing duplicates from the bam files
bsub.py --threads 4 -q long 15 mark04 /nfs/users/nfs_e/ea10/downloaded_software/samtools-1.3/samtools rmdup 5582STDY7771004.fixmatep.bam 5582STDY7771004.markdup.bam
bsub.py --threads 4 -q long 15 mark06 /nfs/users/nfs_e/ea10/downloaded_software/samtools-1.3/samtools rmdup 5582STDY7759906.fixmatep.bam 5582STDY7759906.markdup.bam

bsub.py --threads 4 -q long 15 fix06 /nfs/users/nfs_e/ea10/downloaded_software/samtools-1.3/samtools fixmate 5582STDY7759906.SORTED.bam 5582STDY7759906.fixmate.bam
bsub.py --threads 4 -q long 15 fix06s /nfs/users/nfs_e/ea10/downloaded_software/samtools-1.3/samtools sort -o 5582STDY7759906.fixmatep.bam 5582STDY7759906.fixmate.bam

#Anaconda location installation
/nfs/users/nfs_j/jt24/anaconda3

picard AddOrReplaceReadGroups I=reads.bam O=reads.tag.bam RGID=4 RGLB=lib1 RGPL=ILLUMINA RGPU=unit1 RGSM=20

bsub.py --threads 4 -q normal 15 RGtag04 java -jar picard.jar AddOrReplaceReadGroups I=5582STDY7771004.markdup.bam \
    O=5582STDY7771004.tag.markdup.bam RGID=1 RGLB=lib1 RGPL=ILLUMINA RGPU=unit1 RGSM=5582STDY7771004

bsub.py --threads 4 -q normal 15 RGtag06 java -jar picard.jar AddOrReplaceReadGroups I=5582STDY7759906.markdup.bam \
    O=5582STDY7759906.tag.markdup.bam RGID=1 RGLB=lib1 RGPL=ILLUMINA RGPU=unit1 RGSM=5582STDY7759906

bsub.py --threads 4 -q long 15 last2 gatk --java-options "-Xmx15G" \
    CombineGVCFs -R Ref_nohap/Sm_v7_nohap.fa -V 5582STDY7771004.g.vcf -V 5582STDY7759906.g.vcf -O last2.g.vcf

bsub.py --threads 4 -q long 15 try2 gatk --java-options "-Xmx15G" \
    CombineGVCFs -R Ref_nohap/Sm_v7_nohap.fa -V 5582STDY7724271.combined.renamed.g.vcf -V 5582STDY7724268.combined.renamed.g.vcf -O try2.g.vcf

bsub.py --threads 3 -q long 13 04gvcf gatk --java-options "-Xmx13G" HaplotypeCaller -R Ref_nohap/Sm_v7_nohap.fa \
                                                                            -I 5582STDY7771004.tag.markdup.bam -ERC GVCF -O 5582STDY7771004.g.vcf

bsub.py --threads 3 -q long 13 06gvcf gatk --java-options "-Xmx13G" HaplotypeCaller -R Ref_nohap/Sm_v7_nohap.fa \
                                                                            -I 5582STDY7759906.tag.markdup.bam -ERC GVCF -O 5582STDY7759906.g.vcf

# Sibship analysis#
bsub.py --threads 3 -q long 10 sibship ~jc17/software/vcftools_0.1.15/vcftools --vcf Bi_174_new.recode.vcf --plink-tped
bsub.py --threads 3 -q long 10 sib plink --tfile out --make-bed --out 174_sib
/lustre/scratch118/infgen/team133/sd21/software/KINSHIP/king -b 174_sib.bed --kinship --ibs
bsub.py --threads 3 -q long 10 king /lustre/scratch118/infgen/team133/sd21/software/KINSHIP/king -b 174_sib.bed --kinship --ibs --related
bsub.py --threads 3 -q long 10 king /lustre/scratch118/infgen/team133/sd21/software/KINSHIP/king -b 174_sib.bed --related  # highly recommended
bsub.py --threads 3 -q long 10 king /lustre/scratch118/infgen/team133/sd21/software/KINSHIP/king -b 174_sib.bed --kinship --ibs

#minor allele frequencyls
#Filtering only rare alles between variants between {0.1 to o.1}
bcftools view Bi_174_new.recode.vcf -i 'AF≤0.1' -o myRare.vcf

#fixing my vcf for perlscript_zach_popgen
Vcftools –-vcf myRare2.vcf --recode –recode-INFO-all –out myRare2.vcf.filtered

# position for the TRP associated gene in the gff
grep "Smp_125690" Sm_v7.2_all-validated.gff




