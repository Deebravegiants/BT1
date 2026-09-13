# [C] Apache Tika has XXE vulnerability

## Summary
Severity: Critical
Advisory: GHSA-f58c-gq56-vjjf
CVE: CVE-2025-66516
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-12-04
Source: https://github.com/advisories/GHSA-f58c-gq56-vjjf
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika-core` — affected >=1.13 <3.2.2
- Maven: `org.apache.tika:tika-parsers` — affected >=1.13 <2.0.0
- Maven: `org.apache.tika:tika-parser-pdf-module` — affected >=2.0.0 <3.2.2

## Details
Critical XXE in Apache Tika tika-core (1.13-3.2.1), tika-pdf-module (2.0.0-3.2.1) and tika-parsers (1.13-1.28.5) modules on all platforms allows an attacker to carry out XML External Entity injection via a crafted XFA file inside of a PDF. 

This CVE covers the same vulnerability as in CVE-2025-54988. However, this CVE expands the scope of affected packages in two ways. 

First, while the entrypoint for the vulnerability was the tika-parser-pdf-module as reported in CVE-2025-54988, the vulnerability and its fix were in tika-core. Users who upgraded the tika-parser-pdf-module but did not upgrade tika-core to >= 3.2.2 would still be vulnerable. 

Second, the original report failed to mention that in the 1.x Tika releases, the PDFParser was in the "org.apache.tika:tika-parsers" module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66516
- https://cve.org/CVERecord?id=CVE-2025-54988
- https://github.com/apache/tika
- https://lists.apache.org/thread/s5x3k93nhbkqzztp1olxotoyjpdlps9k
