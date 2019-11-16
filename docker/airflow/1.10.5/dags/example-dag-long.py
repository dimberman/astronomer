from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
	'owner': 'airflow',
	'depends_on_past': False,
	'start_date': datetime(2018, 1, 1),
	'email_on_failure': False,
	'email_on_retry': False,
	'retries': 1,
	'retry_delay': timedelta(minutes=5),
}

dag = DAG('test_long_running_tasks',
			max_active_runs=1,
			concurrency=50,
			default_args=default_args)
last = dag
for i in range (1, 40):
	task = BashOperator(
	task_id='sleep-{}-minute'.format(i),
	bash_command='sleep $[ {} * 60 ]s'.format(i),
	dag=dag)