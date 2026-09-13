# [H] SiYuan before v3.8.2 Path Traversal via removeRiffDeck

## Summary
Severity: High
Advisory: CVE-2026-87815
Aliases: GHSA-94vh-rpgr-rpwc
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:H/SA:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87815
Type: osv

## Details
SiYuan versions before v3.8.2 contain a path traversal vulnerability in the /api/riff/removeRiffDeck endpoint that fails to validate the deckID parameter. An authenticated administrator can supply path traversal sequences to delete arbitrary .deck and .cards files outside the workspace directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87815.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-94vh-rpgr-rpwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-87815
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-path-traversal-via-removeriffdeck
