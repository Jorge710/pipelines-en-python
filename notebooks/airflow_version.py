from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import uuid
import time
from notebooks.utils.xml_adapter import XMLAdpater
from notebooks.utils.data_save_factory import DataSaveFactory

# ------------------------
# Functions
# ------------------------

def logging_decorator(func):
    def inner(*args, **kwargs):
        t1 = time.time()
        time.sleep(5)
        print(f"Llamando funcion: {func.__name__}")
        result = func(*args, **kwargs)
        t2 = time.time()
        print(f"Función completada")
        print(f"Tiempo de ejecución: {t2 - t1}")
        return result
    return inner

@logging_decorator
def step1(**context):
    df_list = context["ti"].xcom_pull(task_ids="extract_data")
    results = []
    for df in df_list:
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        df = df[df["payment_method"] == "PayPal"]
        df = df[df["frequency_of_purchases"].isin(["Weekly", "Fortnightly", "bi-weekly"])]
        results.append(df)
    return results

@logging_decorator
def step2(**context):
    df_list = context["ti"].xcom_pull(task_ids="step1")
    results = []
    for df in df_list:
        df = df[["customer_id", "category", "purchase_amount_(usd)"]].groupby(
            ["customer_id", "category"]
        ).sum().reset_index()
        df["rank"] = df.groupby("category")["purchase_amount_(usd)"].rank(
            method="dense", ascending=False
        )
        df = df[df["rank"] == 1]
        results.append(df)
    return results

@logging_decorator
def step3(**context):
    df_list = context["ti"].xcom_pull(task_ids="step2")
    results = []
    for df in df_list:
        values = df[["customer_id", "category"]].to_dict()
        customers = [x for x in values["customer_id"].values()]
        categories = [x for x in values["category"].values()]
        result = list(zip(customers, categories))
        results.append(result)
    return results

@logging_decorator
def step4(**context):
    results = context["ti"].xcom_pull(task_ids="step3")
    for result in results:
        id = uuid.uuid4()
        DataSaveFactory().save_file(save_type="txt", result=result, id=id)

# ------------------------
# DAG Definition
# ------------------------

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "shopping_behavior_pipeline",
    default_args=default_args,
    description="Replicating pipeline with Airflow",
    schedule_interval=None,   # change to "0 6 * * *" for daily runs at 6 AM
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["pipeline", "shopping"],
) as dag:

    def extract_data():
        df1 = XMLAdpater("data/xml/shopping_behavior_2023.xml").get_data()
        df2 = XMLAdpater("data/xml/shopping_behavior_2024.xml").get_data()
        df3 = XMLAdpater("data/xml/shopping_behavior_2025.xml").get_data()
        return [df1, df2, df3]

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
    )

    step1_task = PythonOperator(
        task_id="step1",
        python_callable=step1,
        provide_context=True,
    )

    step2_task = PythonOperator(
        task_id="step2",
        python_callable=step2,
        provide_context=True,
    )

    step3_task = PythonOperator(
        task_id="step3",
        python_callable=step3,
        provide_context=True,
    )

    step4_task = PythonOperator(
        task_id="step4",
        python_callable=step4,
        provide_context=True,
    )

    extract_task >> step1_task >> step2_task >> step3_task >> step4_task