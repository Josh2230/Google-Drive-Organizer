from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import google.auth.transport.requests
import json

# Scopes (minimal needed for Drive metadata)
# Scopes define what level of access the app is requesting 
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

app = FastAPI()

# Path to your client_secret.json
CLIENT_SECRET_FILE = "/Users/joshualee/Google Drive Organizer/client_secret.json"

# After user signs in with Google, Google redirects them back to app
REDIRECT_URI = "http://localhost:8000/oauth2callback"

creds = None

@app.get("/")
def root():
    return {"message": "Google Drive Organizer Backend is running."}

@app.get("/auth")
def auth():
    """
    Loads app credentials from client_secret.json and tells Google
    what scopes (permissions) we are requesting
    After login, Google will redirect the user back to /oauth2callback
    flow.authroization builds a special google login URL with the right
    parameters like Client ID, scopes, redirect URI.
    """
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI

    auth_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)


@app.get("/oauth2callback")
def oauth2callback(code: str):
    """
    
    """
    global creds
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)
    creds = flow.credentials

    # Save token for later
    with open("token.json", "w") as token:
        token.write(creds.to_json())

    return {"message": "Authentication successful. You can now call /list-files."}


@app.get("/list-files")
def list_files():
    global creds

    if not creds:
        # Try loading saved token
        from google.oauth2.credentials import Credentials
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        else:
            return {"error": "Not authenticated. Visit /auth first."}

    service = googleapiclient.discovery.build("drive", "v3", credentials=creds)

    # Query for Google Docs in a folder
    results = service.files().list(
        q="mimeType = 'application/vnd.google-apps.document'",
        fields="files(id, name, createdTime, modifiedTime)",
        pageSize=20
    ).execute()

    files = results.get("files", [])
    return JSONResponse(content=files)
