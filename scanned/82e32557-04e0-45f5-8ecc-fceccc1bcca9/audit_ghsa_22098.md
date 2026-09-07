# [M] Improper Neutralization of Input During Web Page Generation Apache ActiveMQ

## Summary
Severity: Medium
Advisory: GHSA-5jg4-p78r-p5j3
CVE: CVE-2016-6810
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5jg4-p78r-p5j3
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-client` — affected >=5.0.0 <5.14.2

## Details
In Apache ActiveMQ 5.x before 5.14.2, an instance of a cross-site scripting vulnerability was identified to be present in the web based administration console. The root cause of this issue is improper user data output validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6810
- https://github.com/apache/activemq/commit/77b827f
- https://github.com/apache/activemq/commit/c1157fe1f007ee2344a7f0badefa0794c98817cd
- https://github.com/apache/activemq/commit/e16ed24
- https://github.com/apache/activemq
- https://issues.apache.org/jira/browse/AMQ-6468
- https://lists.apache.org/thread.html/924a3a27fad192d711436421e02977ff90d9fc0f298e1efe6757cfbc@%3Cusers.activemq.apache.org%3E
- https://lists.apache.org/thread.html/a859563f05fbe7c31916b3178c2697165bd9bbf5a65d1cf62aef27d2@%3Ccommits.activemq.apache.org%3E
- http://activemq.apache.org/security-advisories.data/CVE-2016-6810-announcement.txt
