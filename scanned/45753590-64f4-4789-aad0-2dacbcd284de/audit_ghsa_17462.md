# [H] memos vulnerability allows the creation of arbitrary accounts

## Summary
Severity: High
Advisory: GHSA-mg56-wc4q-rw4w
CVE: CVE-2025-65795
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-mg56-wc4q-rw4w
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.25.3

## Details
Incorrect access control in the /api/v1/user endpoint of usememos memos v0.25.2 allows unauthorized attackers to create arbitrary accounts via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65795
- https://github.com/usememos/memos/pull/5217
- https://github.com/usememos/memos/commit/769dcd0cf9be83d472829f6e7903b201e42f6b3c
- https://github.com/advisories/GHSA-mg56-wc4q-rw4w
- https://github.com/usememos/memos
- https://herolab.usd.de/usd-2025-0058
- http://memos.com
- http://usememos.com
