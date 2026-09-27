# [M] Delegated OAuth tokens could revoke unrelated OAuth application authorizations

## Summary
Severity: Medium
Advisory: CVE-2026-16045
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-16045
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.6, 10.11.x <= 10.11.21 Mattermost failed to restrict OAuth deauthorization and personal access token management endpoints to direct user sessions, which allowed an OAuth app with a delegated user token to revoke the user's authorizations or tokens for other integrations via account-management endpoints.. Mattermost Advisory ID: MMSA-2026-00704

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16045.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-16045
