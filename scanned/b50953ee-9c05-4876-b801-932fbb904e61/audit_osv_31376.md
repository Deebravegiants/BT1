# [M] Mobile crash via file with specially crafted filename

## Summary
Severity: Medium
Advisory: CVE-2025-0476
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2025-0476
Type: osv

## Details
Mattermost Mobile Apps versions <=2.22.0 fail to properly handle specially crafted attachment names, which allows an attacker to crash the mobile app for any user who opened a channel containing the specially crafted attachment

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0476.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0476
