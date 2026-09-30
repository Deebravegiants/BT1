# [M] Mattermost Server vulnerable to application crash from attacker-generated large response

## Summary
Severity: Medium
Advisory: GHSA-762v-rq7q-ff97
CVE: CVE-2024-47401
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-762v-rq7q-ff97
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20240926115259-20ed58906adc

## Details
Mattermost versions 9.10.x <= 9.10.2, 9.11.x <= 9.11.1 and 9.5.x <= 9.5.9 fail to prevent detailed error messages from being displayed in Playbooks which allows an attacker to generate a large response and cause an amplified GraphQL response which in turn could cause the application to crash by sending a specially crafted request to Playbooks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47401
- https://github.com/advisories/GHSA-762v-rq7q-ff97
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
