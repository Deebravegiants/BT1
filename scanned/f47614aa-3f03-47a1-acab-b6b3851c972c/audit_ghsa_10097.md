# [H] Authenticated Apache ActiveMQ Broker and Apache ActiveMQ users could perform RCE via Jolokia MBeans

## Summary
Severity: High
Advisory: GHSA-rxpj-7qvf-xv32
CVE: CVE-2026-34197
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-rxpj-7qvf-xv32
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-broker` — affected >=0 <5.19.5
- Maven: `org.apache.activemq:activemq-broker` — affected >=6.0.0 <6.2.3
- Maven: `org.apache.activemq:activemq-all` — affected >=0 <5.19.5
- Maven: `org.apache.activemq:activemq-all` — affected >=6.0.0 <6.2.3

## Details
Improper Input Validation, Improper Control of Generation of Code ('Code Injection') vulnerability in Apache ActiveMQ Broker, Apache ActiveMQ.

Apache ActiveMQ Classic exposes the Jolokia JMX-HTTP bridge at /api/jolokia/ on the web console. The default Jolokia access policy permits exec operations on all ActiveMQ MBeans (org.apache.activemq:*), including
BrokerService.addNetworkConnector(String) and BrokerService.addConnector(String). 

An authenticated attacker can invoke these operations with a crafted discovery URI that triggers the VM transport's brokerConfig parameter to load a remote Spring XML application context using ResourceXmlApplicationContext. 
Because Spring's ResourceXmlApplicationContext instantiates all singleton beans before the BrokerService validates the configuration, arbitrary code execution occurs on the broker's JVM through bean factory methods such as Runtime.exec().
This issue affects Apache ActiveMQ Broker: before 5.19.4, from 6.0.0 before 6.2.3; Apache ActiveMQ: .

Users are recommended to upgrade to version 5.19.5 or 6.2.3, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34197
- https://activemq.apache.org/security-advisories.data/CVE-2026-34197-announcement.txt
- https://github.com/apache/activemq
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2026-34197
- http://www.openwall.com/lists/oss-security/2026/04/06/3
