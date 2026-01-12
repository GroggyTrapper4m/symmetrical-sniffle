import azure.functions as func
import requests
import os
import logging
from packaging.version import parse as parse_version

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

app = func.FunctionApp()

@app.route(route="github_pr_auditor", auth_level=func.AuthLevel.FUNCTION)
def github_pr_auditor(req: func.HttpRequest) -> func.HttpResponse:
    payload = req.get_json()
    
    action = payload.get("action")

    
    if action not in ["opened", "synchronize"]:
        return func.HttpResponse("Action not relevant", status_code=200)

    
    repo_full_name = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]
   
    commit_sha = payload["pull_request"]["head"]["sha"]

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    file_url = f"https://api.github.com/repos/{repo_full_name}/contents/requirements.txt?ref={commit_sha}"
    file_resp = requests.get(file_url, headers=headers)
    
    if file_resp.status_code != 200:
        return func.HttpResponse("No requirements.txt found.", status_code=200)

    import base64
    content = base64.b64decode(file_resp.json()["content"]).decode("utf-8")
    
    updates_found = []
    for line in content.splitlines():
        if "==" in line:
            pkg, current_ver = line.strip().split("==")
            pypi_resp = requests.get(f"https://pypi.org/pypi/{pkg}/json").json()
            latest_ver = pypi_resp['info']['version']

            if parse_version(latest_ver) > parse_version(current_ver):
                updates_found.append(f"| {pkg} | {current_ver} | **{latest_ver}** |")

    if updates_found:
        comment_url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        table_body = "### Python Dependency Updates Are Recommended\n| Package | Current | Latest |\n| --- | --- | --- |\n" + "\n".join(updates_found)
        
        requests.post(comment_url, headers=headers, json={"body": table_body})

    return func.HttpResponse("Audit Complete", status_code=200)