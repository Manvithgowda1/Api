from operator import index
from random import randint
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from datetime import datetime

app = FastAPI(root_path="/api/v1")

@app.get("/")
async def read_root():
    return {"Hello": "World"}

#first api project(campaigns)
#data
data=[
    {"campaign_id": 1,
        "name": "Campaign 1",
        "due_date":datetime.now(),
        "created_at": datetime.now()
    },
    {
        "campaign_id": 2,
        "name": "Campaign 2",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    }
]
"""
Campaigns
-campine_id
-name
-due date
-created at

pieces
-piece_id
-campaign_id
-name
-content
-content_type

""" 
@app.get("/campaigns")
async def read_campaigns():
    return {"campaigns": data}

@app.get("/campaigns/{id}")
async def read_campaign(id: int):
    for campaign in data:
        if campaign["campaign_id"] == id:
            return {"campaign": campaign}
    raise HTTPException(status_code=404, detail="Campaign not found")

@app.post("/campaigns")
async def create_campaign(body: dict[str,Any]):
    new: Any= {
        "campaign_id": randint(100, 999),
        "name":body.get("name"),
        "due_date":body.get("due_date"),
        "created_at": datetime.now()
    }
    data.append(new)
    return {"campaign": new}

@app.put("/campaigns/{id}")
async def update_campaign(id: int, body: dict[str,Any]):
    for campaign in data:
        if campaign["campaign_id"] == id:
            updated: Any={ 
                "campaign_id": id,
                "name": body.get("name"),
                "due_date": body.get("due_date"),
                "created_at": campaign.get("created_at")
            }
            return {"campaign": updated}
    raise HTTPException(status_code=404, detail="Campaign not found") 

@app.delete("/campaigns/{id}")
async def delete_campaign(id: int):
    for index,campaign in enumerate(data):
        if campaign["campaign_id"] == id:
            data.pop(index)
            return Response(status_code=204)        
    raise HTTPException(status_code=404, detail="Campaign not found")    
