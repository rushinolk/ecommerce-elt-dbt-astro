# Olist Data Pipeline: Engenharia de Dados com dbt, Airflow (Cosmos) e AWS

## 📖 Sobre o Projeto
Este projeto simula um ambiente real de Engenharia de Dados utilizando o dataset público de e-commerce brasileiro (Olist). O objetivo principal não foi apenas movimentar dados, mas construir um pipeline robusto focado em **Qualidade de Dados (Data Quality)** e **Governança**.

O pipeline consome dados brutos (CSV), trata inconsistências reais (nulos, duplicatas, erros de tipagem) e entrega dados confiáveis e testados em um Data Warehouse na nuvem, utilizando o **dbt** integrado ao **Airflow** via **Astronomer Cosmos**.

---

## 🏗️ Arquitetura (Medallion)

O projeto segue a arquitetura de camadas para garantir organização, rastreabilidade e performance:

1.  **Bronze (Raw):** Ingestão dos arquivos CSV originais, convertidos para formato otimizado e carregados no **AWS RDS (PostgreSQL)**.
2.  **Silver (Trusted):**
    * Limpeza e padronização de nomes de colunas.
    * **Tipagem Forte:** Conversão de strings para `TIMESTAMP`, `NUMERIC` e `INT` via SQL `CAST`.
    * **Regras de Negócio:** Criação de colunas calculadas como `dias_ate_aprovacao` e `tempo_entrega_real`.
    * **Tratamento de Nulos:** Aplicação de regras de *fallback* (ex: `COALESCE`) para dados incompletos.
3.  **Gold (Analytics):**
    * **Modelagem Dimensional:** Criação de tabelas Fato e Dimensões prontas para BI.
    * **Deduplicação:** Unificação de cadastros de clientes para garantir visão única.

---

## 🛠️ Tech Stack

* **Linguagem:** Python 3.9+ & SQL
* **Transformação & Testes:** dbt Core (Data Build Tool)
* **Orquestração:** Apache Airflow (via Astronomer Cosmos)
* **Banco de Dados:** AWS RDS (PostgreSQL)
* **Infraestrutura:** Docker & Docker Compose

---

## ✨ Destaques Técnicos

### 1. Tratamento de Data Quality (Camada Silver)
Dados reais raramente vêm limpos. Implementei estratégias de saneamento diretamente no SQL:
* **Categorias Nulas:** Produtos sem categoria foram tratados via `COALESCE(category, 'outros')` para evitar "buracos" nas análises de BI.
* **Datas:** Conversão explícita de texto para `TIMESTAMP` para permitir cálculos precisos de SLA logístico.

### 2. Testes Automatizados de Integridade (dbt Tests)
Para garantir a confiabilidade do Data Warehouse, configurei testes automáticos no `schema.yml` que rodam a cada execução do pipeline:
* **`not_null`:** Garante que chaves primárias e IDs vitais nunca sejam nulos.
* **`relationships`:** Assegura a integridade referencial entre a Tabela Fato (Pedidos) e as Dimensões (Clientes, Produtos), impedindo que um pedido referencie um cliente inexistente.

### 3. Deduplicação de Clientes (SCD Type 1)
Um desafio comum no dataset do Olist é a duplicidade de clientes. Utilizei *Window Functions* para aplicar a lógica de manter apenas o registro mais recente:

```sql
/* Exemplo da lógica de deduplicação */
ROW_NUMBER() OVER(
    PARTITION BY customer_unique_id 
    ORDER BY customer_id DESC
) as rn
... WHERE rn = 1

### 4. Orquestração como Código (Cosmos)
Utilizei o **Astronomer Cosmos** para integrar o dbt ao Airflow. Isso permite que o Airflow renderize automaticamente cada modelo dbt como uma Task individual no grafo (DAG), respeitando as dependências definidas nas `refs` do SQL.

---

## 🚀 Como Executar Localmente

### Pré-requisitos
* Docker e Astro CLI instalados.
* Git instalado.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/rushinolk/ecommerce-elt-dbt-astro.git](https://github.com/rushinolk/ecommerce-elt-dbt-astro.git)
    cd olist-data-pipeline
    ```

2.  **Configure as Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz do projeto com as credenciais do banco de dados (exemplo):
    ```env
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=sua_senha
    POSTGRES_HOST=seu_endpoint_rds_ou_local
    POSTGRES_DB=olist
    ```

3.  **Suba o Ambiente:**
    ```bash
    docker-compose up -d
    ```

4.  **Acesse o Airflow:**
    Abra `http://localhost:8080` no navegador (login/senha padrão: `admin`/`admin`). Ative a DAG `olist_dbt_dag` para iniciar o processamento.

---

## 📊 Próximos Passos
* [ ] Construção de Dashboard no Power BI conectado à camada Gold.
* [ ] Implementação de alertas automáticos (Slack/Email) em caso de falha nos testes do dbt.
* [ ] CI/CD para deploy automático dos modelos dbt.

---

### 📬 Contato
Gostou do projeto? Vamos conectar!
* [LinkedIn](https://www.linkedin.com/in/arthur-gomes1/)
