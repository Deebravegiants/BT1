# [H] Improper Input Validation in Apache Qpid AMQP 0-x JMS

## Summary
Severity: High
Advisory: GHSA-f38p-mq64-h784
CVE: CVE-2016-4974
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f38p-mq64-h784
Type: github-advisory

## Affected
- Maven: `org.apache.qpid:qpid-jms-client` — affected >=0 <0.10.0

## Details
Apache Qpid AMQP 0-x JMS client before 6.0.4 and JMS (AMQP 1.0) before 0.10.0 does not restrict the use of classes available on the classpath, which might allow remote authenticated users with permission to send messages to deserialize arbitrary objects and execute arbitrary code by leveraging a crafted serialized object in a JMS ObjectMessage that is handled by the getObject function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4974
- https://issues.apache.org/jira/browse/QPIDJMS-188
- http://packetstormsecurity.com/files/137749/Apache-Qpid-Untrusted-Input-Deserialization.html
- http://qpid.apache.org/components/jms/security-0-x.html
- http://qpid.apache.org/components/jms/security.html
