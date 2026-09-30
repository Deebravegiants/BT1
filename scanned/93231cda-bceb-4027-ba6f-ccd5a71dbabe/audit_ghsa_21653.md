# [H] Apache ActiveMQ Artemis Uncontrolled Resource Consumption (DoS)

## Summary
Severity: High
Advisory: GHSA-pr38-qpxm-g88x
CVE: CVE-2022-23913
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-06
Source: https://github.com/advisories/GHSA-pr38-qpxm-g88x
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:artemis-core-client` — affected >=0 <2.19.1

## Details
In Apache ActiveMQ Artemis prior to 2.20.0 or 2.19.1, an attacker could partially disrupt availability (DoS) through uncontrolled resource consumption of memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23913
- https://github.com/github/codeql-java-CVE-coverage/issues/1061
- https://github.com/apache/activemq-artemis/pull/3862
- https://github.com/apache/activemq-artemis/pull/3862/commits/1f92368240229b8f5db92a92a72c703faf83e9b7
- https://github.com/apache/activemq-artemis/pull/3871
- https://github.com/apache/activemq-artemis/pull/3871/commits/153d2e9a979aead8dff95fbc91d659ecc7d0fb82
- https://github.com/apache/activemq-artemis
- https://issues.apache.org/jira/browse/ARTEMIS-3593
- https://lists.apache.org/thread/fjynj57rd99s814rdn5hzvmx8lz403q2
- https://security.netapp.com/advisory/ntap-20220303-0003
