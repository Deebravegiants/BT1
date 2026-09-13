# [H] Stack Overflow in Apache Mesos

## Summary
Severity: High
Advisory: GHSA-p2xq-vcm7-xjj6
CVE: CVE-2018-11793
CWE: CWE-119
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-03-06
Source: https://github.com/advisories/GHSA-p2xq-vcm7-xjj6
Type: github-advisory

## Affected
- Maven: `org.apache.mesos:mesos` — affected >=0 <1.4.3
- Maven: `org.apache.mesos:mesos` — affected >=1.5.0 <1.5.2
- Maven: `org.apache.mesos:mesos` — affected >=1.6.0 <1.6.2
- Maven: `org.apache.mesos:mesos` — affected >=1.7.0 <1.7.1

## Details
When parsing a JSON payload with deeply nested JSON structures, the parser in Apache Mesos versions pre-1.4.x, 1.4.0 to 1.4.2, 1.5.0 to 1.5.1, 1.6.0 to 1.6.1, and 1.7.0 might overflow the stack due to unbounded recursion. A malicious actor can therefore cause a denial of service of Mesos masters rendering the Mesos-controlled cluster inoperable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11793
- https://github.com/advisories/GHSA-p2xq-vcm7-xjj6
- https://lists.apache.org/thread.html/9be975c53e5ad612c7e0af39f5b88837fbfbc32108e587d3d8499844@%3Cdev.mesos.apache.org%3E
- http://www.securityfocus.com/bid/107281
