params.reads = "$projectDir/example/full_length.fa"
params.emu_database = "$projectDir/emu_database"
params.outdir = "$projectDir/results"

ch_paired = Channel.fromFilePairs("$projectDir/example/*_{f,r}.fq", flat: true)

log.info """\
    EMU IN NEXTFLOW???
    ===================================
    reads        : ${params.reads}
    outdir       : ${params.outdir}
    """
    .stripIndent(true)

ch_paired.view()

process EMU_ABUNDANCE_SR {
    publishDir params.outdir, mode: 'copy'
    input:
    tuple val(prefix), path(read1), path(read2)

    output:
    path "results/*_rel-abundance.tsv", emit: ch

    script:
    """
        export EMU_DATABASE_DIR=${params.emu_database}
        emu abundance --type sr $read1 $read2
    """
    /*
        """
        curl https://codeload.github.com/treangenlab/emu/tar.gz/master | tar -xz --strip=1 emu-master/emu_database
        """
    */
}

process EMU_ABUNDANCE {
    publishDir params.outdir, mode: 'copy'
    input:
    path read

    output:
    path "results/*_rel-abundance.tsv", emit: ch

    script:
    """
        export EMU_DATABASE_DIR=${params.emu_database}
        emu abundance $read
    """
    /*
        """
        curl https://codeload.github.com/treangenlab/emu/tar.gz/master | tar -xz --strip=1 emu-master/emu_database
        """
    */
}

workflow {
    EMU_ABUNDANCE_SR(ch_paired).view()
    EMU_ABUNDANCE(params.reads).view()
}
