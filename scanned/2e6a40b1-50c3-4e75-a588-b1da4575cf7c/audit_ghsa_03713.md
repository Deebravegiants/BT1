# [C] Vulnerability that affects org.springframework.ws:spring-ws and org.springframework.ws:spring-xml

## Summary
Severity: Critical
Advisory: GHSA-8222-6fc8-mhvf
CVE: CVE-2019-3773
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-25
Source: https://github.com/advisories/GHSA-8222-6fc8-mhvf
Type: github-advisory

## Affected
- Maven: `org.springframework.ws:spring-ws` — affected >=0 <2.4.4
- Maven: `org.springframework.ws:spring-ws` — affected >=3.0.0 <3.0.6
- Maven: `org.springframework.ws:spring-xml` — affected >=0 <2.4.4
- Maven: `org.springframework.ws:spring-xml` — affected >=3.0.0 <3.0.6

## Details
Spring Web Services, versions 2.4.3, 3.0.4, and older unsupported versions of all three projects, were susceptible to XML External Entity Injection (XXE) when receiving XML data from untrusted sources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3773
- https://github.com/advisories/GHSA-8222-6fc8-mhvf
- https://pivotal.io/security/cve-2019-3773
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2021.html
