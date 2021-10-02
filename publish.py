import asyncio
import pika
import asyncio

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

properties = pika.BasicProperties('order')
channel = connection.channel()

channel.queue_declare(queue='hello')


channel.basic_publish(exchange='', routing_key='hello',
                      body='Hello World!', properties=properties)

print(" [x] Sent 'Hello World!'")

# connection.close()
