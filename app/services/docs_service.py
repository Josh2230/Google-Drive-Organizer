import googleapiclient.discovery
from app.auth.google_auth import load_credentials
from app.models.response_models import FileListResponse, DriveFile

class Docs:
    def __init__(self):
        self.service = None

    def build_drive_service(self):
        """
        build the drive api service so other functions can call it when needed to 
        create and get what they need from google drive api
        """
        if self.service:
            return self.service
        creds = load_credentials()
        if not creds:
            raise RuntimeError("No credentials available")
        
        # build our google drive api service: creates a client service for a Google API
        # drive: specifies that we are working with google drive api
        # v3: version 3 of the drive api
        self.service = googleapiclient.discovery.build("drive", "v3", credentials=creds)
        return self.service


    def list_drive_files(self) -> FileListResponse:
        """
        Load credentials from respective user
        List first 20 Google Docs across the entire Drive.
        """

        # results gather google documents only with limited fields that we need so we don't overload our json data
        results = self.service.files().list(
            # only google docs and only files that were not trashed
            q="mimeType='application/vnd.google-apps.document' and trashed=false and 'root' in parents",
            # fields that we want to extract
            fields="files(id, name, createdTime, modifiedTime, owners)",
            pageSize=1,
        ).execute()

        # get a list of files that contains data from the fields
        files = results.get("files", [])

        # Convert raw dict -> Pydantic model
        drive_files = [DriveFile(**f) for f in files]

        # return FileListResponse model
        return FileListResponse(files=drive_files)

    def create_folder(self, year):

        # set metadata so we create a google drive folder with the year as name
        file_metadata = {
            'name': str(year),
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # create the folder with 3 required fields that we can access
        folder = self.service.files().create(body=file_metadata, fields="id, name, createdTime").execute()
        
        # convert folder to a DriveFile pydantic model
        drive_file = DriveFile(**folder)
        # Wrap in FileListResponse
        return FileListResponse(files=[drive_file])

    def move_files(self, file, parent):
        """
        Move files function is responsible for moving the file that we find (will always be in root folder for now)
        and we move it to the new parent which will be the folder that has the year the doc was created
        """
        # File is in root (guaranteed by query), so just move it
        updated = self.service.files().update(
            fileId=file.id,
            addParents=parent.id,
            removeParents="root",
            fields="id, parents"
        ).execute()

        print(f"Moved {file.name} -> {parent.name}, new parents: {updated.get('parents')}")

    def find_folder(self, new_folder_name):
        """
        Find the specific folder based on the folder name. We use this in case
        we have already created the folder because google drive allows for repeated names
        """
        query = f"name = '{new_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(
            q = query,
            fields="files(id, name, createdTime, modifiedTime, owners)"
        ).execute()

        items = results.get('files', [])
        if items:
            return DriveFile(**items[0])
        return None


    def create_folders_by_date(self):
        """
        create folders by date will list all the google docs files we find and 
        will check if the user owns it first, and use the year it was created to create
        new folders based on the year as the name and move the google doc we found to that folder
        """

        creds = load_credentials()
        if not creds:
            return FileListResponse(files=[])
        
        # build our google drive api service: creates a client service for a Google API
        # drive: specifies that we are working with google drive api
        # v3: version 3 of the drive api
        service = googleapiclient.discovery.build("drive", "v3", credentials=creds)
        
        files = self.list_drive_files()
        grouped_by_years = {}
        folders = []

        # loop through all the files and check if user owns it
        for f in files.files:
            if not any(owner.get("me") for owner in getattr(f, "owners", [])):
                print(f"Skipping {f.name} (not owned by you)")
                continue
            
            # create a dictionary with years as keys and add files that were created at that year
            year = f.createdTime.year
            if year not in grouped_by_years:
                grouped_by_years[year] = []
            grouped_by_years[year].append(f)
        
        # create folders based on unique year
        for year, docs in grouped_by_years.items():
            # if the folder does not exist, create it, else don't create it
            # and just move the file
            folder_obj = self.find_folder(str(year))
            if not folder_obj:
                new_folder = self.create_folder(year)
                folder_obj = new_folder.files[0]
            else:
                print(f"Using existing folder {year}")
            # folder_response = create_folder(year, service)
            folders.append(folder_obj)
            for doc in docs:
                try:
                    self.move_files(doc, folder_obj)
                    print(f"Moved {doc.name} -> {year}")
                except Exception as e:
                    # skip files that fail (shared files, insufficient permissions, etc.)
                    print(f"Failed to move {doc.name}: {e}")

        return FileListResponse(files=folders)


    def undo(self):
        #TODO after moving files and creating folders by date, add the original parents, and current parents
        # to a file (JSON or csv) so we can have it on standby for when the user clicks undo, we will be able
        # to revert what we just did. Set original parents to current parents and remove current parents
        return