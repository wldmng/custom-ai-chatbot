from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

import os
import json

class ServiceBus():
    client = None
    
    def __init__(self):
        self.client = ServiceBusClient.from_connection_string(conn_str=os.environ['SERVICEBUS_CONNECTION_URL'], logging_enable=True)
        
    async def send_message(self, data, queue_name):
        async with self.client:
            sender = self.client.get_queue_sender(queue_name=queue_name)
                
            async with sender:
                message = ServiceBusMessage(json.dumps(data))
                await sender.send_messages(message)

servicebus_client = ServiceBus()