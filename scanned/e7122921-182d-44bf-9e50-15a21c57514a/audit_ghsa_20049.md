# [M] sememos/memos vulnerable to Improper Handling of Values

## Summary
Severity: Medium
Advisory: GHSA-42q2-m54f-jh95
CVE: CVE-2022-4851
CWE: CWE-229
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-12-29
Source: https://github.com/advisories/GHSA-42q2-m54f-jh95
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.1

## Details
In usememos/memos 0.9.0 and prior, an attacker can post malicious content to another user's memos page via POST request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4851
- https://github.com/usememos/memos/commit/3556ae4e651d9443dc3bb8a170dd3cc726517a53
- https://github.com/usememos/memos
- https://huntr.dev/bounties/e3cebc1a-1326-4a08-abad-0414a717fa0f
