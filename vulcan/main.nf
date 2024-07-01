params.reads = "$projectDir/vulcan-master-test/test/test_reads.fa"
params.reference = "$projectDir/vulcan-master-test/test/GCF_000146045.2_R64_genomic.fna"
params.outdir = "$projectDir/results"
params.percentile = 90

log.info """\
    VULCAN IN NEXTFLOW???
    ===================================
    reads        : ${params.reads}
    reference    : ${params.reference}
    outdir       : ${params.outdir}
    """
    .stripIndent(true)


process VULCAN {
    publishDir params.outdir, mode: 'copy'
    input:
    path reads
    path reference
    val percentile

    output:
    path "vulcan_${percentile}.bam", emit: ch

    script:
    """
        vulcan -i $reads -r $reference -p $percentile -o vulcan
    """
    /*
        """
        curl "https://gitlab.com/treangenlab/vulcan/-/archive/master/vulcan-master.tar?path=test"
        | tar xvz
        """
    */
}

workflow {
    VULCAN(params.reads, params.reference, params.percentile).view()
}
