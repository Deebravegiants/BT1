# [M] Member promoted to channel admin via playbooks run linking to channel

## Summary
Severity: Medium
Advisory: CVE-2024-31859
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-05-26
Source: https://osv.dev/vulnerability/CVE-2024-31859
Type: osv

## Details
Mattermost versions 9.5.x <= 9.5.3, 9.6.x <= 9.6.1 and 8.1.x <= 8.1.12 fail to perform proper authorization checks which allows a member running a playbook in an existing channel to be promoted to a channel admin

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31859.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31859
