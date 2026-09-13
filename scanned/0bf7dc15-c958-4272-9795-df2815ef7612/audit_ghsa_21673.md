# [C] Remote code execution in Apache TomEE

## Summary
Severity: Critical
Advisory: GHSA-mp28-rq7g-qx62
CVE: CVE-2020-13931
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-mp28-rq7g-qx62
Type: github-advisory

## Affected
- Maven: `org.apache.tomee:apache-tomee` — affected >=8.0.0 <8.0.4
- Maven: `org.apache.tomee:apache-tomee` — affected >=7.1.0 <7.1.4
- Maven: `org.apache.tomee:apache-tomee` — affected >=0 <7.0.9

## Details
If Apache TomEE 8.0.0-M1 - 8.0.3, 7.1.0 - 7.1.3, 7.0.0-M1 - 7.0.8, 1.0.0 - 1.7.5 is configured to use the embedded ActiveMQ broker, and the broker config is misconfigured, a JMX port is opened on TCP port 1099, which does not include authentication. CVE-2020-11969 previously addressed the creation of the JMX management interface, however the incomplete fix did not cover this edge case.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13931
- https://lists.apache.org/thread.html/r7f98907165b355dc65f28a57f15103a06173ce03261115fa46d569b4@%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r85b87478f8aa4751aa3a06e88622e80ffabae376ee7283e147ee56b9@%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/ref088c4732e1a8dd0bbbb96e13ffafcfe65f984238ffa55f438d78fe%40%3Cdev.tomee.apache.org%3E
