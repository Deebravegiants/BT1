# [H] Apache ActiveMQ's default configuration doesn't secure the API web context

## Summary
Severity: High
Advisory: GHSA-gj5m-m88j-v7c3
CVE: CVE-2024-32114
CWE: CWE-1188
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-gj5m-m88j-v7c3
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:apache-activemq` — affected >=6.0.0 <6.1.2

## Details
In Apache ActiveMQ 6.x, the default configuration doesn't secure the API web context (where the Jolokia JMX REST API and the Message REST API are located). It means that anyone can use these layers without any required authentication. Potentially, anyone can interact with the broker (using Jolokia JMX REST API) and/or produce/consume messages or purge/delete destinations (using the Message REST API).

To mitigate, users can update the default conf/jetty.xml configuration file to add authentication requirement:
<bean id="securityConstraintMapping" class="org.eclipse.jetty.security.ConstraintMapping">
  <property name="constraint" ref="securityConstraint" />
  <property name="pathSpec" value="/" />
</bean>

Or we encourage users to upgrade to Apache ActiveMQ 6.1.2 where the default configuration has been updated with authentication by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-32114
- https://github.com/apache/activemq/pull/1201
- https://github.com/apache/activemq/commit/43cc596219b6a8c8b5a54fbda3fb68cb4424f2d0
- https://activemq.apache.org/security-advisories.data/CVE-2024-32114-announcement.txt
- https://github.com/apache/activemq
- https://issues.apache.org/jira/browse/AMQ-9477
