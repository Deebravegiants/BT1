# [M] memos vulnerable to Server-Side Request Forgery and Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-9cqm-mgv9-vv9j
CVE: CVE-2024-29029
CWE: CWE-79, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-9cqm-mgv9-vv9j
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.22.0

## Details
memos is a privacy-first, lightweight note-taking service. In memos 0.13.2, an SSRF vulnerability exists at the `/o/get/image` that allows unauthenticated users to enumerate the internal network and retrieve images. The response from the image request is then copied into the response of the current server request, causing a reflected XSS vulnerability. Version 0.22.0 of memos removes the vulnerable file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29029
- https://github.com/usememos/memos/commit/bbd206e8930281eb040cc8c549641455892b9eb5
- https://github.com/usememos/memos
- https://github.com/usememos/memos/blob/06dbd8731161245444f4b50f4f9ed267f7c3cf63/api/v1/http_getter.go#L29
- https://securitylab.github.com/advisories/GHSL-2023-154_GHSL-2023-156_memos
