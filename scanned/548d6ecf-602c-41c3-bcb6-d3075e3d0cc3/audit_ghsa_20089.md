# [M] usememos/memos vulnerable Improper Restriction of Excessive Authentication Attempts 

## Summary
Severity: Medium
Advisory: GHSA-qrrf-xvcf-p64q
CVE: CVE-2022-4797
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-qrrf-xvcf-p64q
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.1

## Details
In usememos/memos 0.9.0 and prior, an attacker can delete other users' posts via post id, which can be done via brute force.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4797
- https://github.com/usememos/memos/commit/3556ae4e651d9443dc3bb8a170dd3cc726517a53
- https://github.com/usememos/memos
- https://huntr.dev/bounties/5233f76f-016b-4c65-b019-2c5d27802a1b
