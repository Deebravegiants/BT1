# [C] Dataease has a JDBC attack vulnerability in the Impala datasource

## Summary
Severity: Critical
Advisory: CVE-2025-58046
Aliases: GHSA-mvwc-x8x9-46c3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-58046
Type: osv

## Details
Dataease is an open-source data visualization and analysis platform. In versions up to and including 2.10.12, the Impala data source is vulnerable to remote code execution due to insufficient filtering in the getJdbc method of the io.dataease.datasource.type.Impala class. Attackers can construct malicious JDBC connection strings that exploit JNDI injection and trigger RMI deserialization, ultimately enabling remote command execution. The vulnerability can be exploited by editing the data source and providing a crafted JDBC connection string that references a remote configuration file, leading to RMI-based deserialization attacks. This issue has been patched in version 2.10.13. It is recommended to upgrade to the latest version. No known workarounds exist for affected versions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58046.json
- https://github.com/dataease/dataease/security/advisories/GHSA-mvwc-x8x9-46c3
- https://nvd.nist.gov/vuln/detail/CVE-2025-58046
- https://github.com/dataease/dataease/commit/8d04e92d44e1bac9284e9e64df5afd7f96d9373c
