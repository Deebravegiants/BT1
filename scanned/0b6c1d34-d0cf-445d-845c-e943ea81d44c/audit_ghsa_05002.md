# [M] Apache ActiveMQ Broker, Apache ActiveMQ, Apache ActiveMQ All have an Exposure of Sensitive Information Through Metadata vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hf52-78x8-6w3w
CVE: CVE-2026-49270
CWE: CWE-1230
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-hf52-78x8-6w3w
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:apache-activemq` — affected >=0 <5.19.7
- Maven: `org.apache.activemq:apache-activemq` — affected >=6.0.0 <6.2.6
- Maven: `org.apache.activemq:activemq-broker` — affected >=0 <5.19.7
- Maven: `org.apache.activemq:activemq-broker` — affected >=6.0.0 <6.2.6
- Maven: `org.apache.activemq:activemq-all` — affected >=0 <5.19.7
- Maven: `org.apache.activemq:activemq-all` — affected >=6.0.0 <6.2.6

## Details
Exposure of Sensitive Information Through Metadata vulnerability in Apache ActiveMQ Broker, Apache ActiveMQ, Apache ActiveMQ All.

Brokers that are configured with a network connector with syncDurableSubs set to true, are vulnerable to an unauthenticated attacker who can receive a list of all durable topic subscriptions in the broker, including client identifiers, subscription names, topic destinations, and JMS selector expressions, by sending a BrokerInfo command. The broker incorrectly responds without first ensuring the connection is authenticated.

This issue affects Apache ActiveMQ Broker: before 5.19.7, from 6.0.0 before 6.2.6; Apache ActiveMQ: before 5.19.7, from 6.0.0 before 6.2.6; Apache ActiveMQ All: before 5.19.7, from 6.0.0 before 6.2.6.

Users are recommended to upgrade to version 6.2.6 or 5.19.7, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49270
- https://github.com/apache/activemq
- https://lists.apache.org/thread/k3233c1x506z3w7x4z0dqvd86d4v2fr2
- http://www.openwall.com/lists/oss-security/2026/05/31/22
