# [M] Unescaped exception messages in error responses in Jetty

## Summary
Severity: Medium
Advisory: GHSA-5h9j-q6j2-253f
CVE: CVE-2019-17632
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-5h9j-q6j2-253f
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.21.v20190926 <9.4.24.v20191120
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.22.v20191022 <9.4.24.v20191120
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.23.v20191118 <9.4.24.v20191120

## Details
In Eclipse Jetty versions 9.4.21.v20190926, 9.4.22.v20191022, and 9.4.23.v20191118, the generation of default unhandled Error response content (in text/html and text/json Content-Type) does not escape Exception messages in stacktraces included in error output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17632
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=553443
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SAITZ27GKPD2CCNHGT2VBT4VWIBUJJNS
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
