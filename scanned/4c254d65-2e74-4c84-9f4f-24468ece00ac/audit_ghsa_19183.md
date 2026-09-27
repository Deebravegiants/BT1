# [C] Mattermost allows reading arbitrary files

## Summary
Severity: Critical
Advisory: GHSA-v469-7wp6-7cvp
CVE: CVE-2025-20051
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-24
Source: https://github.com/advisories/GHSA-v469-7wp6-7cvp
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250122165010-4ed702ccff4e
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0-rc1 <9.11.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.2.0-rc1 <10.2.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.3.0-rc1 <10.3.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0-rc1 <10.4.2

## Details
Mattermost versions 10.4.x <= 10.4.1, 9.11.x <= 9.11.7, 10.3.x <= 10.3.2, 10.2.x <= 10.2.2 fail to properly validate input when patching and duplicating a board, which allows a user to read any arbitrary file on the system via duplicating a specially crafted block in Boards.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-20051
- https://github.com/mattermost/mattermost-plugin-boards/commit/025ce8d363a054473bc002f43f602a4032d38c06
- https://github.com/mattermost/mattermost/commit/4ed702ccff4ec3c9eff832a9b6060f9f4454141d
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
