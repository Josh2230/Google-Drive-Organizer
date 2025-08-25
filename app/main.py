from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.auth import google_auth
from app.services import drive_service
from app.models.response_models import FileListResponse

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Google Drive Organizer Backend is running."}


@app.get("/auth")
def auth():
    """Step 1: Redirect user to Google OAuth consent screen."""
    auth_url = google_auth.get_auth_url()
    return RedirectResponse(auth_url)


@app.get("/oauth2callback")
def oauth2callback(code: str):
    """Step 2: Google redirects here with ?code=... → exchange for tokens."""
    google_auth.exchange_code_for_token(code)
    return {"message": "Authentication successful. You can now call /list-files."}


@app.get("/list-files", response_model=FileListResponse)
def list_files():
    """List Google Docs in Drive."""
    return drive_service.list_drive_files()

##TODO
#app.get("/organize")
