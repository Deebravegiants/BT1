# [M] Insufficient validation of guest board admin privileges on archive import

## Summary
Severity: Medium
Advisory: CVE-2026-16044
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-16044
Type: osv

## Details
Mattermost versions 11.7.x <= 11.7.6, 10.11.x <= 10.11.21 fail to prevent guest users from receiving Board Admin privileges during board archive import which allows a board member to escalate a guest user to Board Admin via importing a crafted .boardarchive file. Mattermost Advisory ID: MMSA-2026-00672

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16044.json
- https://mattermost.com/security-updates
- https://nvd.nist.gov/vuln/detail/CVE-2026-16044
