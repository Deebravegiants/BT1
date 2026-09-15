# [M] Insufficient Authorization On Unlinked Channel Files

## Summary
Severity: Medium
Advisory: CVE-2024-9155
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-09-26
Source: https://osv.dev/vulnerability/CVE-2024-9155
Type: osv

## Details
Mattermost versions 9.10.x <= 9.10.1, 9.9.x <= 9.9.2, 9.5.x <= 9.5.8 fail to limit access to channels files that have not been linked to a post which allows an attacker to view them in channels that they are a member of.

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9155.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9155
