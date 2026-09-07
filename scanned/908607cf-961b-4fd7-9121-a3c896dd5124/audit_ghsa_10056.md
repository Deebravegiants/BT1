# [H] Apache ActiveMQ Vulnerable to Improper Input Validation and Code Injection

## Summary
Severity: High
Advisory: GHSA-w3w2-mpp5-92gm
CVE: CVE-2026-40466
CWE: CWE-20, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-w3w2-mpp5-92gm
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:apache-activemq` — affected >=0 <5.19.6
- Maven: `org.apache.activemq:activemq-all` — affected >=0 <5.19.6
- Maven: `org.apache.activemq:activemq-broker` — affected >=0 <5.19.6
- Maven: `org.apache.activemq:apache-activemq` — affected >=6.0.0 <6.2.5
- Maven: `org.apache.activemq:activemq-all` — affected >=6.0.0 <6.2.5
- Maven: `org.apache.activemq:activemq-broker` — affected >=6.0.0 <6.2.5

## Details
Improper Input Validation, Improper Control of Generation of Code ('Code Injection') vulnerability in Apache ActiveMQ Broker, Apache ActiveMQ All, Apache ActiveMQ.



An authenticated attacker may bypass the fix in CVE-2026-34197 by adding a connector using an HTTP Discovery transport via BrokerView.addNetworkConnector or BrokerView.addConnector through Jolokia if the activemq-http module is on the classpath.
A malicious HTTP endpoint can return a VM transport through the HTTP URI which will bypass the validation added in CVE-2026-34197. The attacker can then use the VM transport's brokerConfig parameter to load a remote Spring XML application context using ResourceXmlApplicationContext.
Because Spring's ResourceXmlApplicationContext instantiates all singleton beans before the BrokerService validates the configuration, arbitrary code execution occurs on the broker's JVM through bean factory methods such as Runtime.exec().


This issue affects Apache ActiveMQ Broker: before 5.19.6, from 6.0.0 before 6.2.5; Apache ActiveMQ All: before 5.19.6, from 6.0.0 before 6.2.5; Apache ActiveMQ: before 5.19.6, from 6.0.0 before 6.2.5.

Users are recommended to upgrade to version 5.19.6 or 6.2.5, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40466
- https://activemq.apache.org/security-advisories.data/CVE-2026-34197-announcement.txt
- https://github.com/apache/activemq
