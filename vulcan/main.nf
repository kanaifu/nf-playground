params.reads = "$projectDir/examples/example-data/example.fastq"

log.info """\
    VULCAN IN NEXTFLOW???
    ===================================
    database     : ${params.database}
    taxonomy     : ${params.taxonomy}
    reads        : ${params.reads}
    outdir       : ${params.outdir}
    """
    .stripIndent(true)


process VULCAN {
    publishDir params.outdir, mode: 'copy'

}

workflow {
}
