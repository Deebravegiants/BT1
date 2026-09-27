# [M] Dataease server-side request forgery via unfiltered DB2 JDBC ldap parameter

## Summary
Severity: Medium
Advisory: CVE-2025-58045
Aliases: GHSA-fmq3-6xhc-r845
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-58045
Type: osv

## Details
Dataease is an open source data analytics and visualization platform. In Dataease versions up to 2.10.12, the patch introduced to mitigate DB2 JDBC deserialization remote code execution attacks only blacklisted the rmi parameter. The ldap parameter in the DB2 JDBC connection string was not filtered, allowing attackers to exploit the DB2 JDBC connection string to trigger server-side request forgery (SSRF). In higher versions of Java, ldap deserialization (autoDeserialize) is disabled by default, preventing remote code execution, but SSRF remains exploitable. Versions up to 2.10.12 are affected. The issue is fixed in version 2.10.13. Updating to 2.10.13 or later is recommended. No known workarounds are documented aside from upgrading.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58045.json
- https://github.com/dataease/dataease/security/advisories/GHSA-fmq3-6xhc-r845
- https://nvd.nist.gov/vuln/detail/CVE-2025-58045
- https://github.com/dataease/dataease/commit/77078658715bd85af5867afbfd5f1fcc37cf03c8
