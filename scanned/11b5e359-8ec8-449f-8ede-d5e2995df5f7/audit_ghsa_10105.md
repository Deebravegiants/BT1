# [M] Mattermost MS Teams plugin doesn't limit the request body size on the /changes webhook endpoint

## Summary
Severity: Medium
Advisory: GHSA-5rfv-h47g-xj42
CVE: CVE-2026-24661
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-5rfv-h47g-xj42
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost-plugin-msteams` — affected >=0 <1.15.1-0.20260213190728-6fe4d295592e

## Details
Mattermost Plugins versions <=2.1.3.0 fail to limit the request body size on the {{/changes}} webhook endpoint which allows an authenticated attacker to cause memory exhaustion and denial of service via sending an oversized JSON payload. Mattermost Advisory ID: MMSA-2026-00611.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24661
- https://github.com/mattermost/mattermost-plugin-msteams/commit/6fe4d295592ecc8767d67e69286cbeec01be3210
- https://github.com/mattermost/mattermost-plugin-msteams
- https://github.com/mattermost/mattermost-plugin-msteams/releases/tag/v2.3.2
- https://mattermost.com/security-updates
