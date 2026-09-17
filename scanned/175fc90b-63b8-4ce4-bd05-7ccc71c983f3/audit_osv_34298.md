# [M] Dataease H2 JDBC RCE Bypass

## Summary
Severity: Medium
Advisory: CVE-2025-57772
Aliases: GHSA-v37q-vh67-9rqv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-57772
Type: osv

## Details
DataEase is an open source business intelligence and data visualization tool. Prior to version 2.10.12, there is a H2 JDBC RCE bypass in DataEase. If the JDBC URL meets criteria, the getJdbcUrl method is returned, which acts as the getter for the JdbcUrl parameter provided. This bypasses H2's filtering logic and returns the H2 JDBC URL, allowing the "driver":"org.h2.Driver" to specify the H2 driver for the JDBC connection. The vulnerability has been fixed in version 2.10.12.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57772.json
- https://github.com/dataease/dataease/security/advisories/GHSA-v37q-vh67-9rqv
- https://nvd.nist.gov/vuln/detail/CVE-2025-57772
- https://github.com/dataease/dataease/commit/1644d81dff46272b09570fa1f4a8f83f01f37440
