# [M] DataEase vulnerable to remote code execution via H2 JDBC driver bypass

## Summary
Severity: Medium
Advisory: CVE-2025-62420
Aliases: GHSA-7wcv-j6gc-qc7q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/CVE-2025-62420
Type: osv

## Details
DataEase is a data visualization and analytics platform. In DataEase versions through 2.10.13, a JDBC driver bypass vulnerability exists in the H2 database connection handler. The getJdbc function in H2.java checks if the jdbcUrl starts with jdbc:h2 but returns a separate jdbc field as the actual connection URL. An attacker can provide a jdbcUrl that starts with jdbc:h2 while supplying a different jdbc field with an arbitrary JDBC driver and connection string. This allows an authenticated attacker to trigger arbitrary JDBC connections with malicious drivers, potentially leading to remote code execution. The vulnerability is fixed in version 2.10.14. No known workarounds exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62420.json
- https://github.com/dataease/dataease/security/advisories/GHSA-7wcv-j6gc-qc7q
- https://nvd.nist.gov/vuln/detail/CVE-2025-62420
- https://github.com/dataease/dataease/commit/bb320e42bf2cf862b9c4b438c1517547b53ed67b
