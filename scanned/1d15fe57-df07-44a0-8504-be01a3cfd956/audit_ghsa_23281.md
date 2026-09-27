# [H] Exposure of Sensitive Information to an Unauthorized Actor in Apache Qpid Broker for Java

## Summary
Severity: High
Advisory: GHSA-8vvh-crqv-jm64
CVE: CVE-2016-8741
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-8vvh-crqv-jm64
Type: github-advisory

## Affected
- Maven: `org.apache.qpid:qpid-broker` — affected >=6.0.0 <6.0.6
- Maven: `org.apache.qpid:qpid-broker` — affected >=6.1.0 <6.1.1

## Details
The Apache Qpid Broker for Java can be configured to use different so called AuthenticationProviders to handle user authentication. Among the choices are the SCRAM-SHA-1 and SCRAM-SHA-256 AuthenticationProvider types. It was discovered that these AuthenticationProviders in Apache Qpid Broker for Java 6.0.x before 6.0.6 and 6.1.x before 6.1.1 prematurely terminate the SCRAM SASL negotiation if the provided user name does not exist thus allowing remote attacker to determine the existence of user accounts. The Vulnerability does not apply to AuthenticationProviders other than SCRAM-SHA-1 and SCRAM-SHA-256.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8741
- https://issues.apache.org/jira/browse/QPID-7599
- http://qpid.2158936.n2.nabble.com/CVE-2016-8741-Apache-Qpid-Broker-for-Java-Information-Leakage-td7657025.html
- http://www.securityfocus.com/bid/95136
- http://www.securitytracker.com/id/1037537
