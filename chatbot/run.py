import os

def run_tool(name):
    exit_code = os.system(f"nextflow run --outdir $PWD/{name}-results ../{name}/main.nf")
    print(f"Running {name} with exit code {exit_code}")
    return exit_code, os.getcwd() + f"/{name}-results"