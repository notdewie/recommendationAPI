import errno
import os
from flask import Flask, request
import logging
from werkzeug.utils import secure_filename
from datetime import datetime
import pika
from dotenv import dotenv_values

config = dotenv_values(".env")  

UPLOAD_FOLDER = config.get('UPLOAD_FOLDER')

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(filename="app.log",
                    format='%(asctime)s %(message)s',
                    filemode='a')
logger = logging.getLogger('app_logger')
logger.setLevel(logging.DEBUG)

uploads_dir = os.path.join(app.root_path, 'uploads')

try:
    os.makedirs(uploads_dir)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

@app.route("/test")
def hello():
    return "Hello World!"

@app.route("/webhook", methods=['POST'])
def webhook():
    return "Execute success!!!"

@app.route("/file", methods=['POST'])
def uploadFiles():
    # get the uploaded file
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        ct = datetime.now().timestamp()
        fileName = secure_filename(str(ct)+"-"+uploaded_file.filename)
        uploaded_file.save(os.path.join(uploads_dir, fileName))
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.get('RABBITMQ_HOST')))
        channel = connection.channel()
        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=fileName,
            properties=pika.BasicProperties(
                delivery_mode=2, 
            ))
        connection.close()
    return "OKLA"

if __name__ == '__main__':
    app.run()
