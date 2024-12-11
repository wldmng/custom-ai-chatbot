from openai import OpenAI
from util.servicebus import servicebus_client

import azure.functions as func
import logging
import json


app = func.FunctionApp()
client = OpenAI()


@app.service_bus_queue_trigger(arg_name="msg", queue_name="process-request-queue",
                               connection="SERVICEBUS_CONNECTION_URL") 
async def process_request(msg: func.ServiceBusMessage):
    message = json.loads(msg.get_body().decode('utf-8'))
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "질문에 대해서 한국어로 대답해."},
            {"role": "user", "content": message['content']}
        ]
    )
    
    answer_data = {
        "channel_id": message['channel_id'],
        "content": completion.choices[0].message.content,
        "type": "answer"
    }
    
    await servicebus_client.send_message(answer_data, 'process-response-queue')

    logging.info(completion.choices[0].message.content)