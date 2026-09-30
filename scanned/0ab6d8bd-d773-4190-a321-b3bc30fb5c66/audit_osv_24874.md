# [M] Deactivated user can retain access using oauth2 api

## Summary
Severity: Medium
Advisory: CVE-2023-2788
CVSS: 6.2 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-2788
Type: osv

## Details
Mattermost fails to check if an admin user account active after an oauth2 flow is started, allowing an attacker with admin privileges to retain persistent access to Mattermost by obtaining an oauth2 access token while the attacker's account is deactivated.

## References
- https://mattermost.com/security-updates/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2788.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2788
