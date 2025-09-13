import os
import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials

# Constants (could also move to utils/config.py later)
SCOPES = ["https://www.googleapis.com/auth/drive"]
CLIENT_SECRET_FILE = os.getenv("GOOGLE_CLIENT_SECRET", "client_secret.json")
REDIRECT_URI = "http://localhost:8000/oauth2callback"

# Global creds (mimic DB for now with token.json)
creds = None
TOKEN_FILE = "token.json"


def get_flow():
    """
    Create a new OAuth flow object with client secrets + scopes.
    Flow is an object from google_auth_oauthlib that handles the oauth2
    process for you. Set the flow.redirect_uri so google knows where to send the user back
    """
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    return flow


def get_auth_url():
    """
    Generate Google OAuth consent screen URL for the user to consent to. 
    The flow object manages the entire OAuth process: generating the authorization URL, 
    exchanging the code, and eventually holding credentials.
    """
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt="consent")
    return auth_url


def exchange_code_for_token(code: str):
    """
    Exchange auth code for long term token and save to token.json. Currently saved in a file
    but would want to use some sort of database in the future. creds is a Credentials object (google.oauth2.credentials.Credentials).
    It contains: access_token: short-lived token to call Google APIs.
    refresh_token: long-lived token (if granted) used to request new access tokens without asking the user again.
    expiry: datetime when the access token expires.
    scopes: list of permissions granted.
    creds.to_json(), saves all that info so we can reload it later instead of asking for consent again
    """
    global creds
    flow = get_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

    return creds


def load_credentials():
    """
    Load saved credentials from token.json if available. If it is not available, we have to ask the user to consent again.
    """
    global creds
    if creds:
        return creds
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        return creds
    return None
