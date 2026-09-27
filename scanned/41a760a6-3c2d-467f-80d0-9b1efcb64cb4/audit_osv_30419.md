# [M] Nextcloud Tables has an Authorization Bypass Through User-Controlled Key in Tables

## Summary
Severity: Medium
Advisory: CVE-2024-52511
Aliases: GHSA-4qqp-9h2g-7qg7
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N)
Published: 2024-11-15
Source: https://osv.dev/vulnerability/CVE-2024-52511
Type: osv

## Details
Nextcloud Tables allows users to to create tables with individual columns. By directly specifying the ID of a table or view, a malicious user could blindly insert new rows into tables they have no access to. It is recommended that the Nextcloud Tables is upgraded to 0.8.0.

## References
- https://hackerone.com/reports/2671404
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52511.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-4qqp-9h2g-7qg7
- https://nvd.nist.gov/vuln/detail/CVE-2024-52511
- https://github.com/nextcloud/tables/commit/52846ad81fe192ee977f14c82a229b0d9cdc406c
- https://github.com/nextcloud/tables/pull/1351
