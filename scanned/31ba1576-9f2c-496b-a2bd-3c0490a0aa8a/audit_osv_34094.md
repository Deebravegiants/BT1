# [M] Files: Potential for SQL Injection through File Browse and List Operations

## Summary
Severity: Medium
Advisory: CVE-2025-54790
Aliases: GHSA-rfvq-g9rm-pgqj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2025-08-01
Source: https://osv.dev/vulnerability/CVE-2025-54790
Type: osv

## Details
Files is a module for managing files inside spaces and user profiles. In versions 0.16.9 and below, Files does not have logic to prevent the exploitation of backend SQL queries without direct output, potentially allowing unauthorized data access. This is fixed in version 0.16.10.

## References
- https://github.com/humhub/cfiles/releases/tag/v0.16.10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54790.json
- https://github.com/humhub/cfiles/security/advisories/GHSA-rfvq-g9rm-pgqj
- https://nvd.nist.gov/vuln/detail/CVE-2025-54790
- https://github.com/humhub/cfiles/pull/252
