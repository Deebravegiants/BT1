# [H] langflow has Unauthenticated IDOR on Image Downloads

## Summary
Severity: High
Advisory: GHSA-7grx-3xcx-2xv5
CVE: CVE-2026-33484
CWE: CWE-284, CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-7grx-3xcx-2xv5
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=1.0.0 <1.9.0

## Details
### Summary
The `/api/v1/files/images/{flow_id}/{file_name}` endpoint serves image files without any authentication or ownership check. Any unauthenticated request with a known flow_id and file_name returns the image with HTTP 200.

### Details
`src/backend/base/langflow/api/v1/files.py:138-164` — `download_image` takes `flow_id`: UUID as a bare path parameter with no Depends(get_flow) or `CurrentActiveUser`. All other file routes (`download_file`, `upload_file`, `list_files`, `delete_file`) use `Depends(get_flow)` which enforces both authentication and ownership. There is no global auth middleware on /api/v1; protection is per-endpoint only.

### PoC
```
curl -v "http://localhost:7860/api/v1/files/images/<flow_uuid>/<filename.png>"
# Returns HTTP 200 with image bytes, no auth header required
```

### Impact
Unauthenticated cross-tenant data leak. In a multi-tenant deployment, any attacker who can discover or guess a `flow_id` (UUIDs can be leaked through other API responses) can download any user's uploaded images without credentials.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-7grx-3xcx-2xv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33484
- https://github.com/langflow-ai/langflow
- https://github.com/pypa/advisory-database/tree/main/vulns/langflow/PYSEC-2026-80.yaml
