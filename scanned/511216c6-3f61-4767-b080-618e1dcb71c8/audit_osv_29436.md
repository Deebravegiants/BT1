# [M] User creation date manipulation in POST /api/v4/users

## Summary
Severity: Medium
Advisory: CVE-2024-42411
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-08-22
Source: https://osv.dev/vulnerability/CVE-2024-42411
Type: osv

## Details
Mattermost versions 9.9.x <= 9.9.1, 9.5.x <= 9.5.7, 9.10.x <= 9.10.0, 9.8.x <= 9.8.2 fail to restrict the input in POST /api/v4/users which allows a user to manipulate the creation date in POST /api/v4/users tricking the admin into believing their account is much older.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42411.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42411
