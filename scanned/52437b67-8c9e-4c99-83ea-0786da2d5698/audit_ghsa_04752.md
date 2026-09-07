# [C] Langflow: Unauthenticated file upload leads to DoS (space exhaustion) and information leak

## Summary
Severity: Critical
Advisory: GHSA-x223-p2gf-v735
CVE: CVE-2026-55450
CWE: CWE-200, CWE-306, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:H (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-x223-p2gf-v735
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.9.1

## Details
### Summary
Unauthenticated users can upload any amount of data to the server without any limitations. No need for any prior knowledge, only network access to Langflow.

This can lead to space exhaustion on the server.

In adition, in the response, the absolute path of the uploaded file is reported to the attacker, which is an information leak that can assist in chaining other primitives.

Tested on commit 2d67402b1dbaefcbce85a244d4a6cd5e4bda1cfe

### Details
Code is in `langflow/api/v1/[endpoints.py](http://endpoints.py/)`:
```python
@router.post(
    "/upload/{flow_id}",
    status_code=HTTPStatus.CREATED,
    deprecated=True,
)
async def create_upload_file(
    file: UploadFile,
    flow_id: UUID,
) -> UploadFileResponse:
...
```
As can be seen above, there is no authentication. There is not validation over `flow_id` as well, unlike other endpoints:
```
        flow_id_str = str(flow_id)
        file_path = await asyncio.to_thread(save_uploaded_file, file, folder_name=flow_id_str)
```
Function `save_uploaded_file` saves the file to local file-system.
Suggested fix:
1. Add authentication to route.
2. Only return relative path or filename.

### PoC
PoC:
```bash
curl 'http://localhost:7860/api/v1/upload/<any_uuid>' -F "file=@<any_file>"
```

Example:
```bash
# curl 'http://localhost:7860/api/v1/upload/11111111-1111-1111-1111-111111111111' -F "file=@/tmp/dummy.txt"
{"flowId":"11111111-1111-1111-1111-111111111111","file_path":"/Users/ori/Library/Caches/langflow/11111111-1111-1111-1111-111111111111/9d63c3b5b7623d1fa3dc7fd1547313b9546c6d0fbbb6773a420613b7a17995c8.txt"}
```

### Impact
1. Space exhaustion on server that can lead to Denial-of-Service.
2. Information leak - leakage of absolute path of langflow's cache directory in server.





### Patches
Fixed in **1.9.1** via PR [#12831](https://github.com/langflow-ai/langflow/pull/12831). The deprecated `POST /api/v1/upload/{flow_id}` endpoint now uses the `get_flow` dependency, requiring an authenticated user and flow ownership (returns `404` for missing or cross-user flows), and enforces the `max_file_size_upload` limit (`HTTP 413`) — closing the unauthenticated upload and disk-exhaustion vectors. Upgrade to **1.9.1 or later**.

Note: the response still returns the file's absolute path (`file_path`); after this fix it is only disclosed to the authenticated owner of the flow.


Ori Lahav
Security Researcher @ Rubrik Inc.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-x223-p2gf-v735
- https://github.com/langflow-ai/langflow/pull/12831
- https://github.com/langflow-ai/langflow
