# [M] HTTPX2: Multipart part header injection via unvalidated file Content-Type and custom headers

## Summary
Severity: Medium
Advisory: CVE-2026-84379
Aliases: GHSA-h4x7-gw46-3wm6, PYSEC-2026-3848
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84379
Type: osv

## Details
HTTPX2 is a next generation HTTP client for Python. Prior to 2.11.0, FileField.render_headers() in src/httpx2/httpx2/_multipart.py directly interpolates attacker-controlled content_type values and custom headers from the files= three-element (filename, content, content_type) tuple and the files= four-element (filename, content, content_type, headers) tuple into multipart/form-data part headers without validating header names or values. CR or LF characters can terminate a part header, inject additional part headers, or end the part header block early, allowing a downstream multipart parser to treat attacker-supplied lines as genuine headers and potentially alter part semantics or bypass header-based checks. This issue is fixed in version 2.11.0.

## References
- https://github.com/pydantic/httpx2/releases/tag/v2.11.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84379.json
- https://github.com/pydantic/httpx2/security/advisories/GHSA-h4x7-gw46-3wm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-84379
- https://github.com/pydantic/httpx2/commit/de96d810ee4e309d118982fe7084a46a2bcd600d
- https://github.com/pydantic/httpx2/pull/1142
