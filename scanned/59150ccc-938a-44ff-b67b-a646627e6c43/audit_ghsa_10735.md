# [H]  Apache ActiveMQ: Denial of Service via Out of Memory vulnerability

## Summary
Severity: High
Advisory: GHSA-5568-6qcg-g7fx
CVE: CVE-2026-39304
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-5568-6qcg-g7fx
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-client` — affected >=0 <5.19.4
- Maven: `org.apache.activemq:activemq-client` — affected >=6.0.0 <6.2.4
- Maven: `org.apache.activemq:activemq-broker` — affected >=0 <5.19.4
- Maven: `org.apache.activemq:activemq-broker` — affected >=6.0.0 <6.2.4
- Maven: `org.apache.activemq:activemq-all` — affected >=0 <5.19.4
- Maven: `org.apache.activemq:activemq-all` — affected >=6.0.0 <6.2.4
- Maven: `org.apache.activemq:apache-activemq` — affected >=0 <5.19.4
- Maven: `org.apache.activemq:apache-activemq` — affected >=6.0.0 <6.2.4

## Details
Denial of Service via Out of Memory vulnerability in Apache ActiveMQ Client, Apache ActiveMQ Broker, Apache ActiveMQ.

ActiveMQ NIO SSL transports do not correctly handle TLSv1.3 handshake KeyUpdates triggered by clients. This makes it possible for a client to rapidly trigger updates which causes the broker to exhaust all its memory in the SSL engine leading to DoS.

Note: TLS versions before TLSv1.3 (such as TLSv1.2) are broken but are not vulnerable to OOM. Previous TLS versions require a full handshake renegotiation which causes a connection to hang but not OOM. This is fixed as well.
This issue affects Apache ActiveMQ Client: before 5.19.4, from 6.0.0 before 6.2.4; Apache ActiveMQ Broker: before 5.19.4, from 6.0.0 before 6.2.4; Apache ActiveMQ: before 5.19.4, from 6.0.0 before 6.2.4.

Users are recommended to upgrade to version 6.2.4 or 5.19.5, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39304
- https://activemq.apache.org/security-advisories.data/CVE-2026-39304-announcement.txt
- https://github.com/apache/activemq
- http://www.openwall.com/lists/oss-security/2026/04/09/17
