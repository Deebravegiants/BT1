# [H] Use after free in Apache Mesos

## Summary
Severity: High
Advisory: GHSA-vpcv-78cp-whr3
CVE: CVE-2017-9790
CWE: CWE-416
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vpcv-78cp-whr3
Type: github-advisory

## Affected
- Maven: `org.apache.mesos:mesos` — affected >=0 <1.1.3
- Maven: `org.apache.mesos:mesos` — affected >=1.2.0 <1.2.2
- Maven: `org.apache.mesos:mesos` — affected >=1.3.0 <1.3.1

## Details
When handling a libprocess message wrapped in an HTTP request, libprocess in Apache Mesos before 1.1.3, 1.2.x before 1.2.2, 1.3.x before 1.3.1, and 1.4.0-dev crashes if the request path is empty, because the parser assumes the request path always starts with '/'. A malicious actor can therefore cause a denial of service of Mesos masters rendering the Mesos-controlled cluster inoperable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9790
- https://lists.apache.org/thread.html/cc1e7a69ea78da0511f5b54b6be7aa6e3c78edad5aaff430e7de028b@%3Cdev.mesos.apache.org%3E
- http://www.securityfocus.com/bid/101023
