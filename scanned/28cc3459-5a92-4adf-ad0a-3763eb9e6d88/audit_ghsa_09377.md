# [M] Mattermost doesn't filter nil elements from outgoing webhook attachment payloads before processing

## Summary
Severity: Medium
Advisory: GHSA-5gmf-x7hg-97wf
CVE: CVE-2026-4915
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-5gmf-x7hg-97wf
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-server` — affected >=11.6.0 <11.6.1
- Go: `github.com/mattermost/mattermost-server` — affected >=11.5.0 <11.5.4
- Go: `github.com/mattermost/mattermost-server` — affected >=11.4.0 <11.4.5
- Go: `github.com/mattermost/mattermost-server` — affected >=10.11.0 <10.11.15
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20260407102538-faa7d75b4ea0

## Details
Mattermost versions 11.6.x <= 11.6.0, 11.5.x <= 11.5.3, 11.4.x <= 11.4.4, 10.11.x <= 10.11.14 fail to filter nil elements from outgoing webhook attachment payloads before processing, which allows an authenticated user to cause a denial of service (server process termination) via a crafted webhook callback response containing a null attachment entry. Mattermost Advisory ID: MMSA-2026-00641

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4915
- https://github.com/mattermost/mattermost/commit/faa7d75b4ea041701e97948f8aa1332e3626a39a
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
