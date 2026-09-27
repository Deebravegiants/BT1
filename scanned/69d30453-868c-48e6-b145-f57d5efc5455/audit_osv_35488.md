# [H] Server-Side Request Forgery (SSRF) in parisneo/lollms

## Summary
Severity: High
Advisory: CVE-2026-0560
Aliases: PYSEC-2026-2199
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-29
Source: https://osv.dev/vulnerability/CVE-2026-0560
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in parisneo/lollms versions prior to 2.2.0, specifically in the `/api/files/export-content` endpoint. The `_download_image_to_temp()` function in `backend/routers/files.py` fails to validate user-controlled URLs, allowing attackers to make arbitrary HTTP requests to internal services and cloud metadata endpoints. This vulnerability can lead to internal network access, cloud metadata access, information disclosure, port scanning, and potentially remote code execution.

## References
- https://huntr.com/bounties/65e43a5e-b902-4369-b738-1825285a3ea5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0560.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0560
- https://github.com/parisneo/lollms/commit/76a54f0df2df8a5b254aa627d487b5dc939a0263
