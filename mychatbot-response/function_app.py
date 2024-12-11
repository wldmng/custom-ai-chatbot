import azure.functions as func
import json

from util.database import db
from util.pubsub import pubsub_client


app = func.FunctionApp()


@app.service_bus_queue_trigger(arg_name="msg", queue_name="process-response-queue",
                               connection="SERVICEBUS_CONNECTION_URL") 
async def process_response_function(msg: func.ServiceBusMessage):
    response = json.loads(msg.get_body().decode('utf-8'))
               
    await db.messages.insert_one(response)
    response['_id'] = str(response['_id'])
    
    await pubsub_client.send_to_group(group=response['channel_id'], message=response)