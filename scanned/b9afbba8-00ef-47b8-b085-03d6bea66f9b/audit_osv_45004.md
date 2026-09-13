# [M] Deactivated user accounts can continue to obtain valid OAuth access tokens via refresh token grant in Mattermost

## Summary
Severity: Medium
Advisory: CVE-2026-9571
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-9571
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.2, 11.6.x <= 11.6.4, 10.11.x <= 10.11.19 fail to invalidate OAuth refresh tokens upon user account deactivation, which allows a deactivated user or an attacker in possession of a valid refresh token to obtain new functional access tokens via the OAuth refresh token grant endpoint.. Mattermost Advisory ID: MMSA-2026-00680

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9571.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-9571
