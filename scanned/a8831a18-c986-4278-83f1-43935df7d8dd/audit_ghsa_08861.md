# [H] Mattermost doesn't sanitize sensitive configuration fields in the Mattermost Calls plugin 

## Summary
Severity: High
Advisory: GHSA-82j6-4fq7-fx62
CVE: CVE-2026-6347
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-82j6-4fq7-fx62
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.2
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.14
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.4
- Go: `github.com/mattermost/mattermost-plugin-calls` — affected >=0 <1.12.0-rc2

## Details
Mattermost versions 11.5.x <= 11.5.1, 10.11.x <= 10.11.13, 11.4.x <= 11.4.3 fail to sanitize sensitive configuration fields in the Mattermost Calls plugin which allows an attacker with access to a support packet to obtain TURN server credentials via the plaintext values present in the exported plugin configuration.. Mattermost Advisory ID: MMSA-2026-00605

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6347
- https://github.com/mattermost/mattermost-plugin-calls/commit/d48893c8558e5a61f5fdd188bbee5ec7cb73887b
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
