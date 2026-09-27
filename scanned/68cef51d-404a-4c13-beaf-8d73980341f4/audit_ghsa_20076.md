# [M] usememos/memos Improper Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hc5q-26h8-r9wf
CVE: CVE-2022-4811
CWE: CWE-285, CWE-639, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-hc5q-26h8-r9wf
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.1

## Details
In usememos/memos 0.9.0 and prior, an unauthorized user can access any private memo by URL hacking a memo on the editing screen.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4811
- https://github.com/usememos/memos/commit/3556ae4e651d9443dc3bb8a170dd3cc726517a53
- https://github.com/usememos/memos
- https://huntr.dev/bounties/e907b754-4f33-46b6-9dd2-0d2223cb060c
