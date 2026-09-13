# [H] Apache ActiveMQ Broker, Apache ActiveMQ All, Apache ActiveMQ have a Code Injection issue

## Summary
Severity: High
Advisory: GHSA-hg6c-8mvr-jqc9
CVE: CVE-2026-42588
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-hg6c-8mvr-jqc9
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-broker` — affected >=0 <5.19.7
- Maven: `org.apache.activemq:activemq-broker` — affected >=6.0.0 <6.2.6
- Maven: `org.apache.activemq:activemq-all` — affected >=0 <5.19.7
- Maven: `org.apache.activemq:activemq-all` — affected >=6.0.0 <6.2.6
- Maven: `org.apache.activemq:apache-activemq` — affected >=0 <5.19.7
- Maven: `org.apache.activemq:apache-activemq` — affected >=6.0.0 <6.2.6

## Details
Improper Input Validation, Improper Control of Generation of Code ('Code Injection') vulnerability in Apache ActiveMQ Broker, Apache ActiveMQ All, Apache ActiveMQ.

Apache ActiveMQ Classic exposes the Jolokia JMX-HTTP bridge at /api/jolokia/ on the web console. The default Jolokia access policy permits exec operations on all ActiveMQ MBeans (org.apache.activemq:*), including
BrokerService.addNetworkConnector(String).

An authenticated attacker can invoke these operations with a crafted discovery URI that triggers the VM transport's brokerConfig parameter using the "masterslave:// " URL which can allow loading a Spring XML application context using ResourceXmlApplicationContext.

Because Spring's ResourceXmlApplicationContext instantiates all singleton beans before the BrokerService validates the configuration, arbitrary code execution occurs on the broker's JVM through bean factory methods such as Runtime.exec().
This issue affects Apache ActiveMQ Broker: before 5.19.7, from 6.0.0 before 6.2.6; Apache ActiveMQ All: before 5.19.7, from 6.0.0 before 6.2.6; Apache ActiveMQ: before 5.19.7, from 6.0.0 before 6.2.6.

Users are recommended to upgrade to version 5.19.7 or 6.2.6, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42588
- https://github.com/apache/activemq
- https://lists.apache.org/thread/ns0zktfo16s9ql2mmtqtlb6p6xcs45xm
- http://www.openwall.com/lists/oss-security/2026/05/31/18
