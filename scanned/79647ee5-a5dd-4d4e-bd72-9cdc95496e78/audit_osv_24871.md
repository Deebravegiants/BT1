# [M] Specially crafted search query can cause large log entries in postgres

## Summary
Severity: Medium
Advisory: CVE-2023-2785
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-06-16
Source: https://osv.dev/vulnerability/CVE-2023-2785
Type: osv

## Details
Mattermost fails to properly truncate the postgres error log message of a search query failure allowing an attacker to cause the creation of large log files which can result in Denial of Service

## References
- https://mattermost.com/security-updates
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2785.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2785
