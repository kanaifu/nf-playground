params.reads = "$projectDir/examples/example-data/example.fastq"
params.database = "$projectDir/examples/example-db"
params.taxonomy = "$projectDir/examples/example-db/taxonomy.tsv"
params.outdir = "$projectDir/results"

log.info """\
    LEMUR IN NEXTFLOW???
    ===================================
    database     : ${params.database}
    taxonomy     : ${params.taxonomy}
    reads        : ${params.reads}
    outdir       : ${params.outdir}
    """
    .stripIndent(true)


process LEMUR {
    publishDir params.outdir, mode: 'copy'

    input:
    path reads
    path database
    path taxonomy

    output:
    path "example-output/*.tsv", emit: ch

    script:
    // curl https://codeload.github.com/treangenlab/lemur/tar.gz/main | \
    // tar -xz --strip=1 lemur-main/examples
    """
    lemur -i $reads \
        -o example-output \
        -d $database \
        --tax-path $taxonomy \
        -r species
    """
}

workflow {
    LEMUR(params.reads, params.database, params.taxonomy).view()
}
