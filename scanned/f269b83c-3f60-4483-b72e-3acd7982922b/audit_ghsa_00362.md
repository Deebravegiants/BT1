# [C] Jetty contains an alias issue that could allow unauthenticated remote code execution due to specially crafted request

## Summary
Severity: Critical
Advisory: GHSA-872g-2h8h-362q
CVE: CVE-2016-4800
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-872g-2h8h-362q
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.3.0 <9.3.9

## Details
The path normalization mechanism in PathResource class in Eclipse Jetty 9.3.x before 9.3.9 on Windows allows remote attackers to bypass protected resource restrictions and other security constraints via a URL with certain escaped characters, related to backslashes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4800
- https://github.com/advisories/GHSA-872g-2h8h-362q
- https://security.netapp.com/advisory/ntap-20190307-0006
- https://www.oracle.com/security-alerts/cpuoct2020.html
- http://dev.eclipse.org/mhonarc/lists/jetty-announce/msg00092.html
- http://www.ocert.org/advisories/ocert-2016-001.html
- http://www.securityfocus.com/bid/90945
- http://www.zerodayinitiative.com/advisories/ZDI-16-362
