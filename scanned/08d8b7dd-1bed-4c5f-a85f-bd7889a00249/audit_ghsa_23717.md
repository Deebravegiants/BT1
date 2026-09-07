# [M] Mortbay Jetty vulnerable to Cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-8h77-9vh5-hw5g
CVE: CVE-2007-5613
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-8h77-9vh5-hw5g
Type: github-advisory

## Affected
- Maven: `org.mortbay.jetty:jetty` — affected >=0 <6.1.6

## Details
Cross-site scripting (XSS) vulnerability in Dump Servlet in Mortbay Jetty before 6.1.6rc1 allows remote attackers to inject arbitrary web script or HTML via unspecified parameters and cookies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-5613
- https://www.redhat.com/archives/fedora-package-announce/2008-July/msg00227.html
- https://www.redhat.com/archives/fedora-package-announce/2008-July/msg00250.html
- http://lists.opensuse.org/opensuse-security-announce/2009-02/msg00002.html
- http://www.kb.cert.org/vuls/id/237888
