# [C] Account TakeOver Due to Improper Handling of JWT Tokens in usememos/memos

## Summary
Severity: Critical
Advisory: GHSA-j2gj-g3p9-7mrr
CVE: CVE-2023-4696
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-01
Source: https://github.com/advisories/GHSA-j2gj-g3p9-7mrr
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.13.2

## Details
Improper Access Control in GitHub repository usememos/memos prior to 0.13.2. As of commit `c9aa2eeb9` access tokens which fail validation are rejected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4696
- https://github.com/usememos/memos/commit/c9aa2eeb9852047e4f41915eb30726bd25f07ecd
- https://huntr.dev/bounties/4747a485-77c3-4bb5-aab0-21253ef303ca
