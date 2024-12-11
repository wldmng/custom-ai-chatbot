from fastapi import FastAPI
from dto.question import QuestionRequest
from fastapi.middleware.cors import CORSMiddleware
from util.servicebus import servicebus_client
from util.pubsub import pubsub_client
from util.database import db
 
import azure.functions as func
import uuid

fast_app = FastAPI()
fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app = func.AsgiFunctionApp(app=fast_app, http_auth_level=func.AuthLevel.ANONYMOUS)


@fast_app.get("/channel-id")
async def get_channel_id():
    return {"channel_id": str(uuid.uuid4())}

@fast_app.post("/question")
async def send_question(request: QuestionRequest):
    question_data = {
        "channel_id": request.channel_id,
        "content": request.content,
        "type": "question"
    }
    
    result = await db.messages.insert_one(question_data)
    question_data['_id'] = str(question_data['_id'])

    await servicebus_client.send_message(question_data, 'process-request-queue')
        
    return str(result.inserted_id)

@fast_app.get("/pubsub/token")
async def read_root(channel_id: str):
    return await pubsub_client.get_client_access_token(groups=[channel_id], minutes_to_expire=5, roles=['webpubsub.joinLeaveGroup.' + channel_id])


