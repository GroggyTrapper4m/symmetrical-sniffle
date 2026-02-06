import azure.functions as func
import requests
import os
import base64
import logging

app = func.FunctionApp()

@app.function_name(name="local_security_check")
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
    
    vulnerability_report_template = """
                        <html>
                        <head>
                        <title>
                         Vuln Report
                        </title>
                        </head>
                        <body>
                        <h2>Dependency Security Audit</h2>
                        <table>
                            <tr><th>Package</th><th>Version</th><th>Sec ID:</th><th>Issue Found</th><th>Summary (if avail)</th></tr>
                            {table_rows}
                        </table>
                        </body>
                        </html>
                        """
    rows = "" 
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
                            print(f"Package: {pkg} | {v['id']} | Summary: {v['summary']}")
                            rows += f"""
                            <tr>
                            <td>{pkg}</td>
                            <td>{ver}</td>
                            <td>{v['id']}</td>
                            <td>{v['details']}</td>
                            <td>{v['summary']}</td>
                            </tr>"""                    
                else:
                    logging.info(f"{pkg}=={ver} is clean.")
            except Exception as e:
                logging.error(f"Error checking {pkg}: {e}")
    
    return func.HttpResponse(
        vulnerability_report_template.format(table_rows=rows),
        mimetype="text/html",
        status_code=200
    )