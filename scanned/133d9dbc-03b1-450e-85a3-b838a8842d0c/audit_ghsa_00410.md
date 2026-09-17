# [H] Apache Qpid Broker-J vulnerable to Denial of Service (DoS) via uncontrolled resource consumption

## Summary
Severity: High
Advisory: GHSA-4r7g-7cpj-5jr7
CVE: CVE-2017-15701
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-4r7g-7cpj-5jr7
Type: github-advisory

## Affected
- Maven: `org.apache.qpid:qpid-broker` — affected >=6.1.0 <6.1.5

## Details
In Apache Qpid Broker-J versions 6.1.0 through 6.1.4 (inclusive) the broker does not properly enforce a maximum frame size in AMQP 1.0 frames. A remote unauthenticated attacker could exploit this to cause the broker to exhaust all available memory and eventually terminate.  Older AMQP protocols are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15701
- https://github.com/advisories/GHSA-4r7g-7cpj-5jr7
- https://github.com/apache/qpid-broker-j
- https://issues.apache.org/jira/browse/QPID-7947
- https://lists.apache.org/thread.html/4054e1c90993f337eeea24a312841c0661653e673c0ff8e2cd9520fe@%3Cdev.qpid.apache.org%3E
- https://qpid.apache.org/cves/CVE-2017-15701.html
- http://www.securityfocus.com/bid/102041
