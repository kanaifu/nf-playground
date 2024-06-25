FROM mambaorg/micromamba:0.25.1

LABEL image.author.name "Marko Tanevski"
LABEL image.author.email "marko@marko.edu"

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yml /tmp/env.yml

RUN micromamba create -n nf-tutorial

RUN micromamba install -y -n nf-tutorial -f /tmp/env.yml && \
    micromamba clean --all --yes

ENV PATH /opt/conda/envs/nf-tutorial/bin:$PATH
