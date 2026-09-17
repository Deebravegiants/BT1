# [C] Dataease PostgreSQL Data Source JDBC Connection Parameters Bypass Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-53005
Aliases: GHSA-99c4-h4fq-r23v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-07-01
Source: https://osv.dev/vulnerability/CVE-2025-53005
Type: osv

## Details
DataEase is an open source business intelligence and data visualization tool. Prior to version 2.10.11, there is a bypass vulnerability in Dataease's PostgreSQL Data Source JDBC Connection Parameters. The sslfactory and sslfactoryarg parameters could trigger a bypass vulnerability. This issue has been patched in version 2.10.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53005.json
- https://github.com/dataease/dataease/security/advisories/GHSA-99c4-h4fq-r23v
- https://nvd.nist.gov/vuln/detail/CVE-2025-53005
