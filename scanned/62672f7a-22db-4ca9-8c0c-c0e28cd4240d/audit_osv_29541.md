# [M] IDOR when marking read a user's channel

## Summary
Severity: Medium
Advisory: CVE-2024-43813
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2024-43813
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.7, 9.10.x <= 9.10.0 fail to enforce proper access controls which allows any authenticated user, including guests, to mark any channel inside any team as read for any user.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43813.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43813
