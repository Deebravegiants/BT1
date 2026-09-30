# [M] Improper Input Validation in Mortbay Jetty 

## Summary
Severity: Medium
Advisory: GHSA-mq4x-8whh-jx73
CVE: CVE-2006-2759
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-mq4x-8whh-jx73
Type: github-advisory

## Affected
- Maven: `org.mortbay.jetty:jetty` — affected >=0 <6.0.0

## Details
jetty 6.0.x (jetty6) beta16 allows remote attackers to read arbitrary script source code via a capital P in the .jsp extension, and probably other mixed case manipulations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-2759
- https://github.com/eclipse/jetty.project
- https://www.eclipse.org/jetty/about.php
