# Google Drive Organizer

A FastAPI backend application to organize Google Docs in Google Drive by their creation year. This tool lists Google Docs, creates folders for each year, and moves the documents into the corresponding folder. Currently, it only handles files in the root directory and avoids nested files.

---

## Features

- OAuth2 authentication with Google.
- Lists Google Docs owned by the authenticated user.
- Creates folders named by the creation year of the documents.
- Moves files from root into the corresponding year folder.
- Avoids touching files already nested in other folders.
- Can later implement undo functionality for moved files.

---

## Technologies Used

- Python 3.11+
- FastAPI
- Google Drive API (`google-api-python-client`)
- Pydantic for data validation
- AnyIO (used internally by FastAPI for async)

---
