# [M] Apache ActiveMQ: Improper validation and restriction of a classpath path name

## Summary
Severity: Medium
Advisory: GHSA-h2h4-5m64-m273
CVE: CVE-2026-33227
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-h2h4-5m64-m273
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-client` — affected >=0 <5.19.3
- Maven: `org.apache.activemq:activemq-client` — affected >=6.0.0 <6.2.2
- Maven: `org.apache.activemq:activemq-broker` — affected >=0 <5.19.3
- Maven: `org.apache.activemq:activemq-broker` — affected >=6.0.0 <6.2.2
- Maven: `org.apache.activemq:activemq-all` — affected >=0 <5.19.3
- Maven: `org.apache.activemq:activemq-all` — affected >=6.0.0 <6.2.2
- Maven: `org.apache.activemq:activemq-web` — affected >=0 <5.19.3
- Maven: `org.apache.activemq:activemq-web` — affected >=6.0.0 <6.2.2

## Details
Improper validation and restriction of a classpath path name vulnerability in Apache ActiveMQ Client, Apache ActiveMQ Broker, Apache ActiveMQ All, Apache ActiveMQ Web, Apache ActiveMQ.

In two instances (when creating a Stomp consumer and also browsing messages in the Web console) an authenticated user provided "key" value could be constructed to traverse the classpath due to path concatenation. As a result, the application is exposed to a classpath path resource loading vulnerability that could potentially be chained together with another attack to lead to exploit. This issue affects Apache ActiveMQ Client: before 5.19.3, from 6.0.0 before 6.2.2; Apache ActiveMQ Broker: before 5.19.3, from 6.0.0 before 6.2.2; Apache ActiveMQ All: before 5.19.3, from 6.0.0 before 6.2.2; Apache ActiveMQ Web: before 5.19.3, from 6.0.0 before 6.2.2; Apache ActiveMQ: before 5.19.3, from 6.0.0 before 6.2.2.

Users are recommended to upgrade to version 5.19.4 or 6.2.3, which fixes the issue. Note: 5.19.3 and 6.2.2 also fix this issue, but that is limited to non-Windows environments due to a path separator resolution bug fixed in 5.19.4 and 6.2.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33227
- https://activemq.apache.org/security-advisories.data/CVE-2026-33227-announcement.txt
- https://github.com/apache/activemq
- http://www.openwall.com/lists/oss-security/2026/04/06/4
