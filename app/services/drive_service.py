import googleapiclient.discovery
from app.auth.google_auth import load_credentials
from app.models.response_models import FileListResponse, DriveFile


def list_drive_files() -> FileListResponse:
    """List first 20 Google Docs across the entire Drive."""
    creds = load_credentials()
    if not creds:
        return FileListResponse(files=[])

    # build our google drive api service
    service = googleapiclient.discovery.build("drive", "v3", credentials=creds)

    # results gather google documents only with limited fields that we need so we don't overload our json data
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.document'",
        fields="files(id, name, createdTime, modifiedTime)",
        pageSize=20,
    ).execute()

    files = results.get("files", [])

    # Convert raw dict → Pydantic model
    drive_files = [DriveFile(**f) for f in files]

    # return FileListResponse model
    return FileListResponse(files=drive_files)
