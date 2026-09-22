# [M] Apache Tomcat Exposes IP Addresses and HTTP Headers of Requests

## Summary
Severity: Medium
Advisory: GHSA-rp8h-vr48-4j8p
CVE: CVE-2011-3375
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rp8h-vr48-4j8p
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=6.0.30 <6.0.35
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0 <7.0.22

## Details
Apache Tomcat 6.0.30 through 6.0.33 and 7.x before 7.0.22 does not properly perform certain caching and recycling operations involving request objects, which allows remote attackers to obtain unintended read access to IP address and HTTP header information in opportunistic circumstances by reading TCP data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-3375
- https://github.com/apache/tomcat/commit/9eae334e9492f55a841e6eb7ab302ff11d03ab21
- https://github.com/apache/tomcat
- http://tomcat.apache.org/security-6.html
- http://tomcat.apache.org/security-7.html
- http://www.debian.org/security/2012/dsa-2401
