from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import ExternalPythonOperator

default_args = {
    'owner': 'juliacygan',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def launch_scraper():
    import sys
    sys.path.append('/Users/juliacygan/homeAlert')
    import scraper

def launch_cleanup():
    import sys
    sys.path.append('/Users/juliacygan/homeAlert')
    import cleanup

with DAG(
    'otodom_scraper_pipeline',
    default_args=default_args,
    description='ETL pipeline for Otodom data, uploading files to S3',
    schedule_interval=None,  
    start_date=datetime(2026, 1, 1),
    catchup=False,                  
    tags=['otodom', 'bronze'],
) as dag:
    run_scraper = ExternalPythonOperator(
        task_id='run_otodom_scraper',
        python='/Users/juliacygan/homeAlert/.venv/bin/python',
        python_callable=launch_scraper
    )
    run_cleanup = ExternalPythonOperator(
        task_id='run_otodom_cleanup',
        python='/Users/juliacygan/homeAlert/.venv/bin/python',
        python_callable=launch_cleanup
    )
    run_scraper >> run_cleanup