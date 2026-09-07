# [M] Owncast Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9355-27m8-h74v
CVE: CVE-2024-31450
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-9355-27m8-h74v
Type: github-advisory

## Affected
- Go: `github.com/owncast/owncast` — affected >=0 <0.1.3

## Details
Owncast is an open source, self-hosted, decentralized, single user live video streaming and chat server. The Owncast application exposes an administrator API at the URL /api/admin. The emoji/delete endpoint of said API allows administrators to delete custom emojis, which are saved on disk. The parameter name is taken from the JSON request and directly appended to the filepath that points to the emoji to delete. By using path traversal sequences (../), attackers with administrative privileges can exploit this endpoint to delete arbitrary files on the system, outside of the emoji directory. This vulnerability is fixed in 0.1.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31450
- https://github.com/owncast/owncast/commit/1b14800c7d7f54be14ed4d130bfe7f480645076e
- https://github.com/owncast/owncast
- https://github.com/owncast/owncast/blob/v0.1.2/controllers/admin/emoji.go#L63
- https://github.com/owncast/owncast/releases/tag/v0.1.3
- https://securitylab.github.com/advisories/GHSL-2023-277_Owncast
