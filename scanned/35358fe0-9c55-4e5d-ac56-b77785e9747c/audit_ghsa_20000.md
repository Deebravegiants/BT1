# [M] usememos/memos has Insufficient Granularity of Access Control

## Summary
Severity: Medium
Advisory: GHSA-7qpw-2j9m-rw8c
CVE: CVE-2022-4813
CWE: CWE-1220
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-7qpw-2j9m-rw8c
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.1

## Details
An Insufficient Granularity of Access Control in usememos/memos prior to 0.9.0 can allow an attacker to delete a memo from the archives.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4813
- https://github.com/usememos/memos/commit/3556ae4e651d9443dc3bb8a170dd3cc726517a53
- https://github.com/usememos/memos
- https://huntr.dev/bounties/a24b45d8-554b-4131-8ce1-f33bf8cdbacc
