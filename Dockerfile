FROM astrocrpublic.azurecr.io/runtime:3.1-5


RUN python -m venv dbt_venv && \
    dbt_venv/bin/pip install --no-cache-dir dbt-core dbt-postgres 