# [H] Apache Tomcat Improper Resource Shutdown or Release vulnerability

## Summary
Severity: High
Advisory: GHSA-gqp3-2cvr-x8m3
CVE: CVE-2025-48989
CWE: CWE-404
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-13
Source: https://github.com/advisories/GHSA-gqp3-2cvr-x8m3
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=11.0.0-M1 <11.0.10
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=10.1.0-M1 <10.1.44
- Maven: `org.apache.tomcat:tomcat-coyote` — affected >=9.0.0.M1 <9.0.108
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=11.0.0-M1 <11.0.10
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=10.1.0-M1 <10.1.44
- Maven: `org.apache.tomcat.embed:tomcat-embed-core` — affected >=9.0.0.M1 <9.0.108

## Details
Improper Resource Shutdown or Release vulnerability in Apache Tomcat made Tomcat vulnerable to the made you reset attack.

This issue affects Apache Tomcat: from 11.0.0-M1 through 11.0.9, from 10.1.0-M1 through 10.1.43 and from 9.0.0.M1 through 9.0.107. Older, EOL versions may also be affected.

Users are recommended to upgrade to one of versions 11.0.10, 10.1.44 or 9.0.108 which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48989
- https://github.com/apache/tomcat/commit/73c04a10395774bda71a0b37802cf983662ce255
- https://github.com/apache/tomcat/commit/f362c8eb3b8ec5b7f312f7f5610731c0fb299a06
- https://github.com/apache/tomcat/commit/f36b8a4eea4ce8a0bc035079e1d259d29f5eb7bf
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://github.com/apache/tomcat
- https://lists.apache.org/thread/9ydfg0xr0tchmglcprhxgwhj0hfwxlyf
- https://tomcat.apache.org/security-10.html
- https://tomcat.apache.org/security-11.html
- https://tomcat.apache.org/security-9.html
- https://www.kb.cert.org/vuls/id/767506
- http://www.openwall.com/lists/oss-security/2025/08/13/2
