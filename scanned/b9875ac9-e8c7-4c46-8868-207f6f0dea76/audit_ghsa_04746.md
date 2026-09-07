# [M] Apache ActiveMQ server has an incomplete authorization workflow

## Summary
Severity: Medium
Advisory: GHSA-cpw7-g3p5-qrfq
CVE: CVE-2026-46605
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-cpw7-g3p5-qrfq
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:apache-activemq` — affected >=0 <5.19.7
- Maven: `org.apache.activemq:apache-activemq` — affected >=6.0.0 <6.2.6

## Details
Incomplete authorization by Apache ActiveMQ server before versions v6.2.6 and v5.19.7 allows authenticated connections to remove existing destinations with proper permissions.

This issue affects Apache ActiveMQ Broker: before 5.19.7, from 6.0.0 before 6.2.6; Apache ActiveMQ All: before 5.19.7, from 6.0.0 before 6.2.6; Apache ActiveMQ: before 5.19.7, from 6.0.0 before 6.2.6.

Users are recommended to upgrade to version v6.2.6 or v5.19.7, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46605
- https://github.com/apache/activemq
- https://lists.apache.org/thread/l4lxgr2s73g9pb218f180psfyskf8ldm
- http://www.openwall.com/lists/oss-security/2026/05/31/20
