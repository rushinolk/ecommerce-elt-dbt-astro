# Olist Data Pipeline: Engenharia de Dados com dbt, Airflow (Cosmos) e AWS

## 📖 Sobre o Projeto

Este projeto implementa um pipeline de dados **ELT (Extract, Load, Transform)** completo utilizando o dataset do E-commerce Olist. O objetivo foi simular um ambiente corporativo moderno, onde a infraestrutura é gerenciada via código e a qualidade dos dados é garantida através de testes automatizados.

O projeto utiliza o **Astro CLI** para gerenciamento do ambiente Airflow e segue uma arquitetura modular: uma DAG dedicada para ingestão de dados brutos (Python) e outra para transformação (dbt), garantindo desacoplamento e facilidade de manutenção.
---

## 🏗️ Arquitetura (Medallion)

O pipeline foi desenhado seguindo a arquitetura **Medallion**, orquestrada em duas etapas distintas:

1.  **Ingestion Layer (DAG `01_ingestion`):**
    * **Setup Database (`setup_database`):** Task inicial que utiliza `PostgresHook` para garantir a limpeza e criação dos schemas (`bronze_olist`, etc.) antes da carga. Isso garante **idempotência**: o pipeline limpa o próprio ambiente antes de começar.
    * Scripts Python extraem os dados brutos (CSV).
    * Converte para o formato parquet e carga na camada **Bronze** no **AWS RDS (PostgreSQL)**.
    * **Trigger Controller:** Ao finalizar o sucesso da carga, utiliza o `TriggerDagRunOperator` para disparar automaticamente a próxima etapa.

3.  **Transformation Layer (DAG `02_transform`):**
    * Disparada automaticamente após o sucesso da ingestão (Dataset/Trigger).
    * O **dbt Core** assume o comando para transformar os dados dentro do banco (ELT).
    * **Silver:** Limpeza (`COALESCE`), tipagem (`CAST`) e padronização.
    * **Gold:** Modelagem dimensional (Fato/Dimensões) e deduplicação de clientes.

---

## 🛠️ Tech Stack

* **Linguagem:** Python 3.9+ & SQL
* **Orquestração & Infra:** Apache Airflow via **Astro CLI**
* **Transformação:** dbt Core (integrado via Cosmos/BashOperator)
* **Banco de Dados:** AWS RDS (PostgreSQL)
* **Gerenciamento de Config:** `airflow_settings.yaml` (Connections as Code)
---

## 📁 Estrutura do Projeto

```text
olist-data-pipeline/
├── dags/
│   ├── 01_ingestion.py       # Extração e Carga (Python Puro)
│   └── 02_transform.py       # Transformação (dbt runner)
├── include/
│   └── dbt/                  # Projeto dbt completo
│       ├── data/             # Dados brutos (CSV)
│       ├── models/           # Modelos de transformação (DBT)
│       ├── data_staging/     # Dados convertidos (PARQUET)
│       ├── tests/            # Testes singulares
│       └── dbt_project.yml
├── tests/                    # Testes unitários do Airflow
├── airflow_settings.yaml     # Configuração automática de conexões
├── Dockerfile                # Customização da imagem Astro Runtime
└── README.md
```

---
## ✨ Destaques Técnicos

### 1. Pipeline Idempotente e Auto-Gerenciável
A task `setup_database` na DAG de ingestão roda comandos DDL (`DROP SCHEMA IF EXISTS` / `CREATE SCHEMA`) antes de qualquer dado ser processado. Isso torna o pipeline **resiliente**: ele garante um estado limpo a cada execução, evitando conflitos ou duplicidade de dados antigos na camada Bronze.

### 2. Arquitetura Desacoplada (Ingestão vs Transformação)
Ao invés de uma DAG monolítica, separei as responsabilidades. A DAG `01_ingestion.py` foca apenas em extrair e carregar o dado bruto. Ao finalizar, ela aciona a `02_transform.py`. Isso facilita o *backfill* e a manutenção: se a regra de negócio muda, rodo apenas a transformação, sem precisar reprocessar a ingestão (API/CSV).

### 3. Data Quality e Testes (dbt)
A confiança no dado é garantida via `schema.yml`. O pipeline falha automaticamente se:
* **Integridade:** Um pedido na tabela fato referenciar um cliente inexistente (`relationships`).
* **Completude:** IDs críticos estiverem nulos (`not_null`).
* **Lógica de Negócio:** Tratamento de categorias nulas (`COALESCE`) e conversão de datas (`CAST`) direto no SQL.

### 4. Gerenciamento de Conexões (IaC)
Eliminei a necessidade de configurar conexões manualmente na interface do Airflow a cada deploy. Utilizei o arquivo `airflow_settings.yaml` para definir as credenciais do **AWS RDS** como código, garantindo que o ambiente suba pronto para uso.

### 5. Deduplicação Avançada (SQL)
Implementação de lógica **SCD Tipo 1** na camada Gold para unificar clientes duplicados, utilizando Window Functions (`ROW_NUMBER`) para priorizar sempre o registro mais recente do cliente.

```sql
/* Exemplo da lógica de deduplicação */
ROW_NUMBER() OVER(
    PARTITION BY customer_unique_id 
    ORDER BY customer_id DESC
) as rn
... WHERE rn = 1
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos
* Docker Desktop instalado e rodando.
* **Astro CLI** instalado (Ferramenta de linha de comando da Astronomer).

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/rushinolk/ecommerce-elt-dbt-astro.git](https://github.com/rushinolk/ecommerce-elt-dbt-astro.git)
    cd olist-data-pipeline
    ```

2.  **Verifique as Conexões:**
    O arquivo `airflow_settings.yaml` já está configurado para criar a conexão `postgres_olist_dw` automaticamente.
    *(Certifique-se de que suas credenciais da AWS ou do Banco Local estejam corretas neste arquivo).*



3.  **Inicie o Ambiente Astro:**
    Este comando irá construir a imagem Docker e subir os containers do Airflow (Webserver, Scheduler, Triggerer e Postgres de metadados).
    ```bash
    astro dev start
    ```

4.  **Acesse o Airflow:**
    Abra `http://localhost:8080` no seu navegador.
    * **Usuário:** `admin`
    * **Senha:** `admin`
    
    Ative a DAG **`01_ingestion`** e acompanhe o fluxo completo até a transformação no dbt.
    

---

## 📊 Próximos Passos
* [ ] Construção de Dashboard no Power BI conectado à camada Gold.

---

### 📬 Contato
Gostou do projeto? Vamos conectar!
* [LinkedIn](https://www.linkedin.com/in/arthur-gomes1/)
