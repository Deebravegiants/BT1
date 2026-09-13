# [M] DataEase vulnerable to JDBC URL injection in DB2 and MongoDB data source configuration

## Summary
Severity: Medium
Advisory: CVE-2025-62419
Aliases: GHSA-x4x9-mjcf-99r9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/CVE-2025-62419
Type: osv

## Details
DataEase is a data visualization and analytics platform. In DataEase versions through 2.10.13, a JDBC URL injection vulnerability exists in the DB2 and MongoDB data source configuration handlers. In the DB2 data source handler, when the extraParams field is empty, the HOSTNAME, PORT, and DATABASE values are directly concatenated into the JDBC URL without filtering illegal parameters. This allows an attacker to inject a malicious JDBC string into the HOSTNAME field to bypass previously patched vulnerabilities CVE-2025-57773 and CVE-2025-58045. The vulnerability is fixed in version 2.10.14. No known workarounds exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62419.json
- https://github.com/dataease/dataease/security/advisories/GHSA-x4x9-mjcf-99r9
- https://nvd.nist.gov/vuln/detail/CVE-2025-62419
- https://github.com/dataease/dataease/commit/bb320e42bf2cf862b9c4b438c1517547b53ed67b
