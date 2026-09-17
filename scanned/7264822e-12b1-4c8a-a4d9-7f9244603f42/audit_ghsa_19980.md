# [H] usememos/memos vulnerable to improper authorization

## Summary
Severity: High
Advisory: GHSA-vwg4-846x-f94v
CVE: CVE-2022-4688
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-23
Source: https://github.com/advisories/GHSA-vwg4-846x-f94v
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.0

## Details
usememos/memos is an open-source, self-hosted memo hub with knowledge management and socialization. Memos versions prior to 0.9.0 are vulnerable to improper authorization, which can allow a user to modify the nickname, username and email of other users without permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4688
- https://github.com/usememos/memos/commit/dca35bde877aab6e64ef51b52e590b5d48f692f9
- https://github.com/usememos/memos
- https://huntr.dev/bounties/23856e7e-94ff-4dee-97d0-0cd47e9b8ff6
