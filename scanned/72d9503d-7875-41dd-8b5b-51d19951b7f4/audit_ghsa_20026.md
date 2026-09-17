# [M] usememos/memos Improper Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pp3p-6jjh-rmg7
CVE: CVE-2022-4806
CWE: CWE-284, CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-pp3p-6jjh-rmg7
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.1

## Details
An Improper Access Control vulnerability in usememos/memos 0.9.0 and prior can result in a user deleting others' public and private memos.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4806
- https://github.com/usememos/memos/commit/3556ae4e651d9443dc3bb8a170dd3cc726517a53
- https://github.com/usememos/memos
- https://huntr.dev/bounties/2c7101bc-e6d8-4cd0-9003-bc8d86f4e4be
