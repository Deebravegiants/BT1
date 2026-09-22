# [C] Mattermost allows reading arbitrary files related to importing boards

## Summary
Severity: Critical
Advisory: GHSA-5fwx-p6xh-vjrh
CVE: CVE-2025-25279
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-24
Source: https://github.com/advisories/GHSA-5fwx-p6xh-vjrh
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20250122165010-4ed702ccff4e
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=9.11.0-rc1 <9.11.8
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.2.0-rc1 <10.2.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.3.0-rc1 <10.3.3
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=10.4.0-rc1 <10.4.2

## Details
Mattermost versions 10.4.x <= 10.4.1, 9.11.x <= 9.11.7, 10.3.x <= 10.3.2, 10.2.x <= 10.2.2 fail to properly validate board blocks when importing boards which allows an attacker could read any arbitrary file on the system via importing and exporting a specially crafted import archive in Boards.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25279
- https://github.com/mattermost/mattermost-plugin-boards/commit/025ce8d363a054473bc002f43f602a4032d38c06
- https://github.com/mattermost/mattermost/commit/4ed702ccff4ec3c9eff832a9b6060f9f4454141d
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
