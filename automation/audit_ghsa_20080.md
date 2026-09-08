# [H] usememos/memos vulnerable to account takeover due to improper access control

## Summary
Severity: High
Advisory: GHSA-w57v-6xp4-rm2v
CVE: CVE-2022-4689
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-23
Source: https://github.com/advisories/GHSA-w57v-6xp4-rm2v
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.0

## Details
usememos/memos is an open-source, self-hosted memo hub with knowledge management and socialization. Versions prior to 0.9.0 improperly maintain access control allowing an attacker to take over an account by changing header values in the HTTP request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4689
- https://github.com/usememos/memos/pull/831
- https://github.com/usememos/memos/commit/dca35bde877aab6e64ef51b52e590b5d48f692f9
- https://github.com/usememos/memos
- https://huntr.dev/bounties/a78c4326-6e7b-47fe-aa82-461e5c12a4e3
