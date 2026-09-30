# [H] Jetty vulnerable to exposure of sensitive information due to observable discrepancy

## Summary
Severity: High
Advisory: GHSA-wfcc-pff6-rgc5
CVE: CVE-2017-9735
CWE: CWE-200, CWE-203
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-wfcc-pff6-rgc5
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.6.v20170531
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.3.0 <9.3.20.v20170531
- Maven: `org.eclipse.jetty:jetty-server` — affected >=0 <9.2.22.v20170606

## Details
Jetty through 9.4.x contains a timing channel attack in `util/security/Password.java`, which allows attackers to obtain access by observing elapsed times before rejection of incorrect passwords.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9735
- https://github.com/eclipse/jetty.project/issues/1556
- https://github.com/eclipse/jetty.project/commit/042f325f1cd6e7891d72c7e668f5947b5457dc02
- https://bugs.debian.org/864631
- https://github.com/eclipse/jetty.project
- https://lists.apache.org/thread.html/053d9ce4d579b02203db18545fee5e33f35f2932885459b74d1e4272@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/36870f6c51f5bc25e6f7bb1fcace0e57e81f1524019b11f466738559@%3Ccommon-dev.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/f887a5978f5e4c62b9cfe876336628385cff429e796962649649ec8a@%3Ccommon-issues.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/ff8dcfe29377088ab655fda9d585dccd5b1f07fabd94ae84fd60a7f8@%3Ccommits.pulsar.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/05/msg00016.html
- https://web.archive.org/web/20170826163336/http://www.securityfocus.com/bid/99104
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
