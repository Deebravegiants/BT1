# [H] Apache Camel JMS deserialization filter bypass

## Summary
Severity: High
Advisory: GHSA-f755-xp6r-8q84
CVE: CVE-2026-43866
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-f755-xp6r-8q84
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-jms` — affected >=3.0.0 <4.14.8
- Maven: `org.apache.camel:camel-jms` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-jms` — affected >=4.19.0 <4.21.0
- Maven: `org.apache.camel:camel-sjms` — affected >=3.0.0 <4.14.8
- Maven: `org.apache.camel:camel-sjms` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-sjms` — affected >=4.19.0 <4.21.0
- Maven: `org.apache.camel:camel-sjms2` — affected >=3.0.0 <4.14.8
- Maven: `org.apache.camel:camel-sjms2` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-sjms2` — affected >=4.19.0 <4.21.0
- Maven: `org.apache.camel:camel-amqp` — affected >=3.0.0 <4.14.8
- Maven: `org.apache.camel:camel-amqp` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-amqp` — affected >=4.19.0 <4.21.0
- Maven: `org.apache.camel:camel-activemq` — affected >=3.0.0 <4.14.8
- Maven: `org.apache.camel:camel-activemq` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-activemq` — affected >=4.19.0 <4.21.0
- Maven: `org.apache.camel:camel-activemq6` — affected >=3.0.0 <4.14.8
- Maven: `org.apache.camel:camel-activemq6` — affected >=4.15.0 <4.18.3
- Maven: `org.apache.camel:camel-activemq6` — affected >=4.19.0 <4.21.0

## Details
Deserialization of Untrusted Data vulnerability in Apache Camel, Apache Camel JMS component.

JmsBinding.extractBodyFromJms() in camel-jms - and the equivalent JmsBinding in camel-sjms - deserializes the payload of an incoming JMS ObjectMessage via jakarta.jms.ObjectMessage.getObject() whenever the mapJmsMessage option is enabled (the default) and Camel acts as a JMS consumer. The CVE-2026-40860 hardening added a post-deserialization class check that rejects classes outside the default allow-list java.**;javax.**;org.apache.camel.**;!*. However org.apache.camel.support.DefaultExchangeHolder itself lives in the allow-listed org.apache.camel.** namespace, so an ObjectMessage whose top-level object is a DefaultExchangeHolder passes the check. The receiving side then calls DefaultExchangeHolder.unmarshal() on it without requiring the transferExchange option to be enabled - an asymmetric trust boundary, since the sending side gates ObjectMessage and transferExchange handling but the receiving side did not - writing every non-null field of the holder into the Exchange: the message body, the IN and OUT headers, the exchange properties, the variables, the exchange id and the exception. An attacker who can publish an ObjectMessage to a queue or topic consumed by an affected Camel application can therefore inject arbitrary Exchange state using only universally-trusted java.lang and java.util types, with no deserialization gadget chain required, to manipulate routing and headers, exchange properties and error handling. The same handling applies to camel-sjms and camel-sjms2, and to the JMS-family components built on JmsComponent and JmsBinding: camel-amqp, camel-activemq and camel-activemq6. This is a bypass of the CVE-2026-40860 fix rather than a flaw in it.
This issue affects Apache Camel: from 3.0.0 before 4.14.8, from 4.15.0 before 4.18.3, from 4.19.0 before 4.21.0; Apache Camel: from 3.0.0 before 4.14.8, from 4.15.0 before 4.18.3, from 4.19.0 before 4.21.0.

Users are recommended to upgrade to version 4.21.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.8. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.3. After upgrading, JMS ObjectMessage handling is disabled by default in camel-jms, camel-sjms and the JMS-family components (a new objectMessageEnabled option defaults to false at the component and endpoint level), so an incoming ObjectMessage - including a DefaultExchangeHolder payload - is no longer deserialized unless the option is explicitly enabled; only set objectMessageEnabled=true when the consumed JMS destination is fed exclusively by trusted producers. For deployments that cannot upgrade immediately, restrict publish access to the queues and topics consumed by Camel to trusted producers via JMS broker authorization, and do not expose JMS consumers that map ObjectMessage bodies to untrusted networks; a JMS-provider deserialization allow-list does not mitigate this specific bypass because the crafted payload uses only universally-trusted classes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-43866
- https://github.com/apache/camel/pull/22970
- https://github.com/apache/camel/pull/22968
- https://github.com/apache/camel/pull/22945
- https://github.com/apache/camel/pull/22920
- https://github.com/apache/camel/pull/22918
- https://github.com/apache/camel/pull/22866
- https://github.com/apache/camel/commit/844bbf8c894c5e2bfa023579db80dcd3354c0e1b
- https://github.com/apache/camel/commit/81449eb6ef3edf856c84117ce708beb2ada8f650
- https://github.com/apache/camel/commit/75d7991b89265a2e8e62c7207165deb88c3a6ef3
- https://github.com/apache/camel/commit/6cb29c0bbd7d1c46f057eac46c4afa62c9f5e00f
- https://github.com/apache/camel/commit/17f8fcb22569f4c459b9e53c1485bfc764dc0015
- https://github.com/apache/camel/commit/01ead5e8473a2b2fca4902c0236978805b990c31
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.14.8
- https://github.com/apache/camel/releases/tag/camel-4.18.3
- https://github.com/apache/camel/releases/tag/camel-4.21.0
- https://issues.apache.org/jira/browse/CAMEL-23373
- https://issues.apache.org/jira/browse/CAMEL-23409
- https://camel.apache.org/security/CVE-2026-43866.html
