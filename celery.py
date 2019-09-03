from __future__ import absolute_import

from celery import Celery
from kombu import Exchange, Queue

class Config:
    #broker_url = 'redis://52.69.43.74:6379/0'
    broker_url = 'redis://:M8Lu9lMONSYZEZAdXTPw0frMhtvl0fkr@redis-11880.c54.ap-northeast-1-2.ec2.cloud.redislabs.com:11880'
    enable_utc = True
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    imports = (
        'RssEmail.sendmail_worker'
    )
    task_queues = (
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('q_sendmail', Exchange('q_sendmail'), routing_key='q_sendmail'),

    )

    task_routes = {
        'RssEmail.worker.sendmail': {'queue': 'q_sendmail', 'routing_key': 'q_sendmail'},
    }

app_rssemail = Celery('rssemail')
app_rssemail.config_from_object(Config)

if __name__ == '__main__':
    app_rssemail.worker_main()