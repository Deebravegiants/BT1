# [H] marker through 2.0.0 Path Traversal via upload filename

## Summary
Severity: High
Advisory: CVE-2026-85684
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85684
Type: osv

## Details
marker through 2.0.0 contains a path traversal vulnerability in the FastAPI /marker/upload handler that fails to sanitize the file.filename parameter. Unauthenticated attackers can supply filenames containing directory traversal sequences to write arbitrary files to any location or delete existing files on the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85684.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85684
- https://www.vulncheck.com/advisories/marker-through-2.0.0-path-traversal-via-upload-filename
- https://github.com/datalab-to/marker/issues/1047
- https://github.com/datalab-to/marker
- https://github.com/datalab-to/marker/blob/v2.0.0/marker/scripts/server.py
