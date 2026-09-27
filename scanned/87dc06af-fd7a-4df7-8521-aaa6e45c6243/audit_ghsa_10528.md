# [C] Apache camel-jms, camel-sjms, camel-sjms2 and camel-amqp: Unsafe Deserialization of JMS ObjectMessage

## Summary
Severity: Critical
Advisory: GHSA-m5vh-3fw5-5wgh
CVE: CVE-2026-40860
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-m5vh-3fw5-5wgh
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-jms` — affected >=3.0.0 <4.14.7
- Maven: `org.apache.camel:camel-jms` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-jms` — affected >=4.19.0 <4.20.0
- Maven: `org.apache.camel:camel-sjms` — affected >=3.0.0 <4.14.7
- Maven: `org.apache.camel:camel-sjms` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-sjms` — affected >=4.19.0 <4.20.0
- Maven: `org.apache.camel:camel-sjms2` — affected >=3.0.0 <4.14.7
- Maven: `org.apache.camel:camel-sjms2` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-sjms2` — affected >=4.19.0 <4.20.0
- Maven: `org.apache.camel:camel-amqp` — affected >=3.0.0 <4.14.7
- Maven: `org.apache.camel:camel-amqp` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-amqp` — affected >=4.19.0 <4.20.0
- Maven: `org.apache.camel:camel-activemq` — affected >=3.0.0 <4.14.7
- Maven: `org.apache.camel:camel-activemq` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-activemq` — affected >=4.19.0 <4.20.0
- Maven: `org.apache.camel:camel-activemq6` — affected >=3.0.0 <4.14.7
- Maven: `org.apache.camel:camel-activemq6` — affected >=4.15.0 <4.18.2
- Maven: `org.apache.camel:camel-activemq6` — affected >=4.19.0 <4.20.0

## Details
JmsBinding.extractBodyFromJms() in camel-jms, and the equivalent JmsBinding class in camel-sjms, deserialized the payload of incoming JMS ObjectMessage values via javax.jms.ObjectMessage.getObject() without applying any ObjectInputFilter, class allowlist or class denylist. Because this code path is reached whenever the mapJmsMessage option is enabled (the default) and Camel acts as a JMS consumer, an attacker able to publish a crafted ObjectMessage to a queue or topic consumed by a Camel application could achieve remote code execution when a deserialization gadget chain was present on the classpath. The same handling was reached transitively through camel-sjms2 (whose Sjms2Endpoint extends SjmsEndpoint) and through camel-amqp (whose AMQPJmsBinding extends JmsBinding), and by other JMS-family components built on JmsComponent such as camel-activemq and camel-activemq6.

This issue affects Apache Camel: from 3.0.0 before 4.14.7, from 4.15.0 before 4.18.2, from 4.19.0 before 4.20.0.

Users are recommended to upgrade to version 4.20.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.7. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40860
- https://github.com/apache/camel/pull/22598
- https://github.com/apache/camel/pull/22603
- https://github.com/apache/camel/pull/22604
- https://github.com/apache/camel/pull/22639
- https://github.com/apache/camel/commit/0c06142c46a1422b6b49fab784a1087c50e48ee8
- https://github.com/apache/camel/commit/107e8c279cf9bf488843e33fb6333cc2d7f37c67
- https://github.com/apache/camel/commit/6a82709f0fc5431f46d2939547aacd2c7395c97a
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40860.json
- https://issues.apache.org/jira/browse/CAMEL-23321
- https://github.com/apache/camel/releases/tag/camel-4.20.0
- https://github.com/apache/camel/releases/tag/camel-4.18.2
- https://github.com/apache/camel/releases/tag/camel-4.14.7
- https://github.com/apache/camel
- https://camel.apache.org/security/CVE-2026-40860.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2463172
- https://access.redhat.com/security/cve/CVE-2026-40860
- https://access.redhat.com/errata/RHSA-2026:22453
- https://access.redhat.com/errata/RHSA-2026:17668
- http://www.openwall.com/lists/oss-security/2026/04/26/10
