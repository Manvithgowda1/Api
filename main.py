
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated, Generic, TypeVar

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True
    )



class CampaignCreate(SQLModel):
    name: str
    due_date: datetime | None = None



T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    data: T



sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}

engine = create_engine(
    sqlite_url,
    connect_args=connect_args,
    echo=True
)



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)



def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables
    create_db_and_tables()

    # Seed database if empty
    with Session(engine) as session:

        existing_campaign = session.exec(
            select(Campaign)
        ).first()

        if not existing_campaign:

            session.add_all([
                Campaign(
                    name="Summer Launch",
                    due_date=datetime.now(timezone.utc)
                ),
                Campaign(
                    name="Black Friday",
                    due_date=datetime.now(timezone.utc)
                )
            ])

            session.commit()

    yield


app = FastAPI(
    title="Campaign Management API",
    version="1.0.0",
    lifespan=lifespan
)

router = APIRouter(prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello World"}

@router.get(
    "/campaigns",
    response_model=APIResponse[list[Campaign]]
)
async def read_campaigns(session: SessionDep):

    data = session.exec(
        select(Campaign)
    ).all()

    return {"data": data}

@router.get(
    "/campaigns/{campaign_id}",
    response_model=APIResponse[Campaign]
)
async def read_campaign(
    campaign_id: int,
    session: SessionDep
):

    data = session.get(Campaign, campaign_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    return {"data": data}

@router.post(
    "/campaigns",
    status_code=201,
    response_model=APIResponse[Campaign]
)
async def create_campaign(
    campaign: CampaignCreate,
    session: SessionDep
):

    db_campaign = Campaign.model_validate(campaign)

    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)

    return {"data": db_campaign}

@router.put(
    "/campaigns/{campaign_id}",
    response_model=APIResponse[Campaign]
)
async def update_campaign(
    campaign_id: int,
    campaign: CampaignCreate,
    session: SessionDep
):

    data = session.get(Campaign, campaign_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    data.name = campaign.name
    data.due_date = campaign.due_date

    session.add(data)
    session.commit()
    session.refresh(data)

    return {"data": data}


@router.delete(
    "/campaigns/{campaign_id}",
    status_code=204
)
async def delete_campaign(
    campaign_id: int,
    session: SessionDep
):

    data = session.get(Campaign, campaign_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    session.delete(data)
    session.commit()


# Register API routes
app.include_router(router)
