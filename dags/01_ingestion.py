import pendulum
import pandas as pd
from pathlib import Path
from datetime import timedelta
from airflow import DAG
from airflow.sdk import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

BASE_DIR = Path("/usr/local/airflow/include")
PATH_DATA = BASE_DIR / "data"
PATH_STAGING = "/usr/local/airflow/include/staging/"



default_args = {
    "depends_on_past" : False,
    "email": ["teste@email.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(seconds=30),
}


with DAG(
    dag_id="dag_ingestion",
    description="Extração e carga para projeto olist",
    default_args=default_args,
    schedule=None,
    start_date=pendulum.datetime(2025,1,1,tz="America/Sao_Paulo"),
    catchup=False,
    tags=["Pratica","Etl"]
) as dag:
    

    @task(task_id='extract_data')
    def task_extract(path_data:str) -> str:

        for arquivo in path_data.iterdir():
            nome_tabela = arquivo.stem
            dataframe = pd.read_csv(arquivo)
            path_parquet = PATH_STAGING+nome_tabela+'.parquet'
            dataframe.to_parquet(path_parquet,index=False)
        
        return PATH_STAGING
    
    @task(task_id='setup_database')
    def setup_database():
        hook = PostgresHook(postgres_conn_id='postgres_olist_dw')
        hook.run("DROP SCHEMA IF EXISTS bronze_olist CASCADE;")
        hook.run("DROP SCHEMA IF EXISTS dbt_arthur_meta CASCADE;")

        hook.run("CREATE SCHEMA IF NOT EXISTS bronze_olist;")
        hook.run("CREATE SCHEMA IF NOT EXISTS dbt_arthur;")


    @task(task_id='load_data')
    def task_load(path_stanging:str):
        hook = PostgresHook(postgres_conn_id='postgres_olist_dw')
        engine = hook.get_sqlalchemy_engine()
        staging = Path(path_stanging)
        staging.mkdir(parents=True,exist_ok=True)


        lista_parquet = staging.glob("*.parquet")

        for arquivo in lista_parquet:
            nome_tabela = arquivo.stem
            df = pd.read_parquet(arquivo)
            df.to_sql(
                name=nome_tabela,
                con=engine,
                schema='bronze_olist',
                if_exists='replace',
                index=False
            )
    
    trigger_transform = TriggerDagRunOperator(
        task_id="trigger_transform",
        trigger_dag_id="dag_transformation", 
        wait_for_completion=True 
    )


    df = task_extract(PATH_DATA)
    [df , setup_database()] >> task_load(df) >> trigger_transform