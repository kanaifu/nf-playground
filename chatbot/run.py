import os

def run_tool(name):
    exit_code = os.system(f"nextflow run --outdir $PWD/{name}-results ../{name}/main.nf")
    return exit_code, os.getcwd() + f"/{name}-results"