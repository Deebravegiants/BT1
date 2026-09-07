# [M] Mattermost Server Path Traversal vulnerability that leads to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-762g-9p7f-mrww
CVE: CVE-2024-46872
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-762g-9p7f-mrww
Type: github-advisory

## Affected
- Go: `github.com/mattermost/mattermost/server/v8` — affected >=0 <8.0.0-20240926115259-20ed58906adc

## Details
Mattermost versions 9.10.x <= 9.10.2, 9.11.x <= 9.11.1, 9.5.x <= 9.5.9 fail to sanitize user inputs in the frontend that are used for redirection which allows for a one-click client-side path traversal that is leading to CSRF in Playbooks

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46872
- https://github.com/advisories/GHSA-762g-9p7f-mrww
- https://github.com/mattermost/mattermost
- https://mattermost.com/security-updates
