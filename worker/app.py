import pika
from handle import execute
from logger import getLogger
from dotenv import dotenv_values
import time

config = dotenv_values(".env")  

SERVICE="Worker"
time.sleep(10)
getLogger().info(f'[{SERVICE}] Connecting to server ...')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.get("RABBITMQ_HOST")))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)
getLogger().info(f'[{SERVICE}] Connected')

getLogger().info(f'[{SERVICE}] Waiting for messages.')

def callback(ch, method, properties, body):
    filename=body.decode()
    getLogger().info(f'[{SERVICE}] Received {filename}')
    getLogger().info(execute(filename))
    getLogger().info(f'[{SERVICE}] Done')
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Listening queue
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)
channel.start_consuming()