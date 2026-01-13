import azure.functions as func
import requests
import os
import base64
import logging

app = func.FunctionApp()

@app.route(route="local_security_check", auth_level=func.AuthLevel.FUNCTION)
def local_security_check(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("--- Starting Security Audit ---")
    
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO = os.getenv("REPOSITORY_NAME")
    BRANCH = os.getenv("BRANCH_NAME")
    
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    file_url = f"https://api.github.com/repos/{REPO}/contents/requirements.txt"
    
    resp = requests.get(file_url, headers=headers, params={"ref": BRANCH})
    if resp.status_code != 200:
        return func.HttpResponse("File not found.", status_code=404)

    content = base64.b64decode(resp.json()["content"]).decode("utf-8")
    lines = content.splitlines()
    
    vulnerability_report = []

   
    for line in lines:
        if "==" in line:
            pkg, ver = line.strip().split("==")
            pypi_url = f"https://pypi.org/pypi/{pkg}/{ver}/json"
            
            try:
                pypi_resp = requests.get(pypi_url).json()
                vulnerabilities = pypi_resp.get("vulnerabilities", [])
                
                if vulnerabilities:
                    logging.warning(f"{pkg}=={ver} is VULNERABLE")
                    for v in vulnerabilities:
                        vulnerability_report.append(f"Package: {pkg} | ID: {v['id']} | Summary: {v['summary'][:100]}...")
                else:
                    logging.info(f"{pkg}=={ver} is clean.")
            except Exception as e:
                logging.error(f"Error checking {pkg}: {e}")

    if vulnerability_report:
        result = "VULNERABILITIES DETECTED:\n" + "\n".join(vulnerability_report)
        return func.HttpResponse(result, status_code=200)
    
    return func.HttpResponse("All packages passed security check.", status_code=200)