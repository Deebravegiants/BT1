# [H] Apache ActiveMQ has an Incorrect Default Permissions vulnerability

## Summary
Severity: High
Advisory: GHSA-99qx-5qqr-4j95
CVE: CVE-2026-49157
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-99qx-5qqr-4j95
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:apache-activemq` — affected >=0 <5.19.7
- Maven: `org.apache.activemq:apache-activemq` — affected >=6.0.0 <6.2.6

## Details
Incorrect Default Permissions vulnerability in Apache ActiveMQ.

This issue affects Apache ActiveMQ: before 5.19.7, from 6.0.0 before 6.2.6.

The default Jolokia authorization settings granted non-admin (low-privilege) web-login accounts access to Jolokia operations which allowed executing broker management operations meant for admins such as addQueue and removeQueue.

Users are recommended to upgrade to version 6.2.6 or 5.19.7, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49157
- https://github.com/apache/activemq
- https://lists.apache.org/thread/rrcsf6s90hj4tdh89nvkko75q5505rj8
- http://www.openwall.com/lists/oss-security/2026/05/31/21
