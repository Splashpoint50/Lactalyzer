
from flask import Flask, render_template, request
import dropbox
import csv
import json
from io import StringIO
from dropbox_config_access_token import APP_KEY, APP_SECRET, REFRESH_TOKEN

app = Flask(__name__)

# Connect to Dropbox
def get_dropbox_client():
    return dropbox.Dropbox(
        app_key=APP_KEY,
        app_secret=APP_SECRET,
        oauth2_refresh_token=REFRESH_TOKEN
    )

# List all session folders
@app.route('/sessions')
def list_sessions():
    dbx = get_dropbox_client()
    folders = []
    res = dbx.files_list_folder('/sessions')
    for entry in res.entries:
        if isinstance(entry, dropbox.files.FolderMetadata):
            folders.append(entry.name)
    return render_template('session_list.html', folders=sorted(folders, reverse=True))

# View specific session
@app.route('/sessions/<session_id>')
def view_session(session_id):
    dbx = get_dropbox_client()
    session_path = f'/sessions/{session_id}'
    csv_data = []
    predictions = {}

    # Get CSV
    try:
        metadata, res = dbx.files_download(f'{session_path}/session_log_{session_id}.csv')
        content = res.content.decode('utf-8')
        reader = csv.reader(StringIO(content))
        csv_data = list(reader)
    except Exception as e:
        csv_data = [["Error loading CSV:", str(e)]]

    # Get JSON
    try:
        metadata, res = dbx.files_download(f'{session_path}/final_result.json')
        predictions = json.loads(res.content)
    except Exception as e:
        predictions = {"error": str(e)}

    return render_template('session_view.html', session_id=session_id, csv_data=csv_data, predictions=predictions)

# Root route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
