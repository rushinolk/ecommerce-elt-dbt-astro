import pendulum
from pathlib import Path
from airflow import DAG
from cosmos import DbtDag, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from cosmos.constants import ExecutionMode

# --- CAMINHO DO PROJETO DBT ---
DBT_PROJECT_DIR = Path("/usr/local/airflow/include/dbt")

DBT_EXECUTABLE_PATH = Path("/usr/local/airflow/dbt_venv/bin/dbt")


profile_config = ProfileConfig(
    profile_name="olist_dbt",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="postgres_olist_dw", # ID da conexão que você criou na UI
        profile_args={"schema": "dbt_arthur"},
    ),
)


dbt_dag = DbtDag(
    # Configurações do Projeto
    project_config=ProjectConfig(dbt_project_path=DBT_PROJECT_DIR),
    profile_config=profile_config,
    
    # Configuração de Execução (A Mágica do Isolamento)
    execution_config=ExecutionConfig(
        execution_mode=ExecutionMode.LOCAL,
        dbt_executable_path=str(DBT_EXECUTABLE_PATH),
    ),
    
    # O que instalar na venv isolada
    operator_args={
        #"py_requirements": ["dbt-core", "dbt-postgres"],
        "install_deps": True, 
    },
    
    # Configurações padrão de DAG do Airflow
    dag_id="dag_transformation",
    schedule=None,
    start_date=pendulum.datetime(2025, 1, 1, tz="America/Sao_Paulo"),
    catchup=False,
    tags=["Olist", "dbt", "Cosmos"],
)