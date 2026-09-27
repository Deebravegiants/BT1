# [M] Apache ActiveMQ Artemis: Passwords leaking from broker properties in the debug log

## Summary
Severity: Medium
Advisory: CVE-2025-27391
Aliases: GHSA-pm4j-p7pm-fpvx
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2025-04-09
Source: https://osv.dev/vulnerability/CVE-2025-27391
Type: osv

## Details
Insertion of Sensitive Information into Log File vulnerability in Apache ActiveMQ Artemis. All the values of the broker properties are logged when the org.apache.activemq.artemis.core.config.impl.ConfigurationImpl logger has the debug level enabled.

This issue affects Apache ActiveMQ Artemis: from 1.5.1 before 2.40.0. It can be mitigated by restricting log access to only trusted users.

Users are recommended to upgrade to version 2.40.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/04/09/3
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27391.json
- https://lists.apache.org/thread/25p96cvzl1mkt29lwm2d8knklkoqolps
- https://nvd.nist.gov/vuln/detail/CVE-2025-27391
