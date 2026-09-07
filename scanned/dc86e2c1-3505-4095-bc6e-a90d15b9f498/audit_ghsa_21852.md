# [H] Missing Authentication for Critical Function in Apache TomEE

## Summary
Severity: High
Advisory: GHSA-836g-5fr5-fgcr
CVE: CVE-2020-11969
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-836g-5fr5-fgcr
Type: github-advisory

## Affected
- Maven: `org.apache.tomee:tomee` — affected >=8.0.0-M1 <8.0.2
- Maven: `org.apache.tomee:tomee` — affected >=7.1.0 <7.1.3
- Maven: `org.apache.tomee:tomee` — affected >=7.0.0-M1 <7.0.8
- Maven: `org.apache.tomee:tomee` — affected >=1.0.0 <1.7.6

## Details
If Apache TomEE is configured to use the embedded ActiveMQ broker, and the broker URI includes the useJMX=true parameter, a JMX port is opened on TCP port 1099, which does not include authentication. This affects Apache TomEE 8.0.0-M1 - 8.0.1, Apache TomEE 7.1.0 - 7.1.2, Apache TomEE 7.0.0-M1 - 7.0.7, Apache TomEE 1.0.0 - 1.7.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11969
- https://lists.apache.org/thread.html/r85b87478f8aa4751aa3a06e88622e80ffabae376ee7283e147ee56b9@%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/rbd23418646dedda70a546331ea1c1d115b8975b7e7dc452d10e2e773%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/rbd23418646dedda70a546331ea1c1d115b8975b7e7dc452d10e2e773@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/ref088c4732e1a8dd0bbbb96e13ffafcfe65f984238ffa55f438d78fe@%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/ref088c4732e1a8dd0bbbb96e13ffafcfe65f984238ffa55f438d78fe@%3Cusers.tomee.apache.org%3E
- http://www.openwall.com/lists/oss-security/2020/12/16/2
