import pdb
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import select

# from sqlalchemy.orm import Session
from sqlmodel import Session

from journal_rss.config import Config
from journal_rss.db import create_tables, get_engine, get_session
from journal_rss.services import crossref
from journal_rss.models import api
from journal_rss import models



app = FastAPI()
config = Config()
engine = get_engine(config)

app.mount('/static', StaticFiles(
    directory=(Path(__file__).parents[1] / 'static').resolve()), name='static')
templates = Jinja2Templates(
    directory=(Path(__file__).parents[1]  / 'templates').resolve()
)

@app.on_event("startup")
def on_startup():
    create_tables(engine)

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})

@app.post('/search')
async def search(request: Request, search: Annotated[str, Form()]):
    """
    Search for a journal using the crossref API
    """
    results = crossref.journal_search(search)
    results = crossref.store_journal(results)

    return templates.TemplateResponse(
        'partials/feed-list.html',
        {
            'request': request,
            'journals': results
        })

