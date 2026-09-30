# [H] usememos/memos makes Incorrect Use of Privileged APIs

## Summary
Severity: High
Advisory: GHSA-ghx2-6v4g-9wmm
CVE: CVE-2022-4796
CWE: CWE-648
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-ghx2-6v4g-9wmm
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.1

## Details
In usememos/memos 0.9.0 and prior, a user with login permission can delete all notes of the whole application via `API DELETE https://demo.usememos.com/api/memo/$idnote`. The vulnerability will lose all user notes data throughout the system, causing damage to user data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4796
- https://github.com/usememos/memos/commit/3556ae4e651d9443dc3bb8a170dd3cc726517a53
- https://github.com/usememos/memos
- https://huntr.dev/bounties/efe8001b-1d6a-41af-a64c-736705cc66a6
