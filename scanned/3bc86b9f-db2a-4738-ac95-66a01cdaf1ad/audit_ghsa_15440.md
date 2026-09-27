# [M] memos vulnerable to Server-Side Request Forgery in /o/get/httpmeta

## Summary
Severity: Medium
Advisory: GHSA-6fcf-g3mp-xj2x
CVE: CVE-2024-29028
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-6fcf-g3mp-xj2x
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.16.1

## Details
memos is a privacy-first, lightweight note-taking service. In memos 0.13.2, an SSRF vulnerability exists at the /o/get/httpmeta that allows unauthenticated users to enumerate the internal network and receive limited html values in json form. This vulnerability is fixed in 0.16.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29028
- https://github.com/usememos/memos/commit/6ffc09d86a1302c384ef085aa70c7bddb3ce7ba9
- https://github.com/usememos/memos
- https://securitylab.github.com/advisories/GHSL-2023-154_GHSL-2023-156_memos
