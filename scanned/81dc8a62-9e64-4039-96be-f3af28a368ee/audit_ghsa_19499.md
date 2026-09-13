# [M] Apache Pulsar Kafka Connector Logs Sensitive Information in Application Logs

## Summary
Severity: Medium
Advisory: GHSA-rcqj-3fmp-5cqx
CVE: CVE-2025-30677
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-rcqj-3fmp-5cqx
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-io-kafka-connect-adaptor` — affected >=0 <3.0.11
- Maven: `org.apache.pulsar:pulsar-io-kafka-connect-adaptor` — affected >=3.3.0 <3.3.6
- Maven: `org.apache.pulsar:pulsar-io-kafka-connect-adaptor` — affected >=4.0.0 <4.0.4
- Maven: `org.apache.pulsar:pulsar-io-kafka` — affected >=0 <3.0.11
- Maven: `org.apache.pulsar:pulsar-io-kafka` — affected >=3.3.0 <3.3.6
- Maven: `org.apache.pulsar:pulsar-io-kafka` — affected >=4.0.0 <4.0.4

## Details
Apache Pulsar contains multiple connectors for integrating with Apache Kafka. The Pulsar IO Apache Kafka Source Connector, Sink Connector, and Kafka Connect Adaptor Sink Connector log sensitive configuration properties in plain text in application logs.


This vulnerability can lead to unintended exposure of credentials in log files, potentially allowing attackers with access to these logs to obtain Apache Kafka credentials. The vulnerability's impact is limited by the fact that an attacker would need access to the application logs to exploit this issue.

This issue affects Apache Pulsar IO's Apache Kafka connectors in all versions before 3.0.11, 3.3.6, and 4.0.4.


3.0.x version users should upgrade to at least 3.0.11.

3.3.x version users should upgrade to at least 3.3.6.

4.0.x version users should upgrade to at least 4.0.4.


Users operating versions prior to those listed above should upgrade to the aforementioned patched versions or newer versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30677
- https://github.com/apache/pulsar/pull/24128
- https://github.com/apache/pulsar
- https://lists.apache.org/thread/zv5fwwrh374r1p5cmksxcd40ssxxko3d
- https://pulsar.apache.org/security
- http://www.openwall.com/lists/oss-security/2025/04/09/2
