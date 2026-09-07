# [M] Apache ActiveMQ webconsole admin GUI is open to XSS

## Summary
Severity: Medium
Advisory: GHSA-cc94-3v9c-7rm8
CVE: CVE-2020-1941
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-05-21
Source: https://github.com/advisories/GHSA-cc94-3v9c-7rm8
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:activemq-web-console` — affected >=5.0.0 <5.15.12

## Details
In Apache ActiveMQ 5.0.0 to 5.15.11, the webconsole admin GUI is open to XSS, in the view that lists the contents of a queue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1941
- https://github.com/apache/activemq/commit/7793a95
- https://github.com/apache/activemq/commit/81bd743eaa243f0cc5dfbb1342cee1fef1fc5df2
- https://github.com/apache/activemq/commit/c0e17a3
- https://github.com/apache/activemq
- https://issues.apache.org/jira/browse/AMQ-7231
- https://lists.apache.org/thread.html/r946488fb942fd35c6a6e0359f52504a558ed438574a8f14d36d7dcd7@%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb2fd3bf2dce042e0ab3f3c94c4767c96bb2e7e6737624d63162df36d@%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/re4672802b0e5ed67c08c9e77057d52138e062f77cc09581b723cf95a@%3Ccommits.activemq.apache.org%3E
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://activemq.apache.org/security-advisories.data/CVE-2020-1941-announcement.txt
