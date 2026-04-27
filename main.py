from fastapi import FastAPI
from fastapi.responses import FileResponse
from supabase import create_client
from openai import OpenAI
import os
import json
import requests

app = FastAPI()

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
