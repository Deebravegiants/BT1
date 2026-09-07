# [C] Mapfish Print: Remote Code Injection (RCE) in Dynamic table

## Summary
Severity: Critical
Advisory: GHSA-q7m6-wpvf-mvwx
CVE: CVE-2026-44672
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-q7m6-wpvf-mvwx
Type: github-advisory

## Affected
- Maven: `org.mapfish.print:print-lib` — affected >=3.23.0 <3.28.28
- Maven: `org.mapfish.print:print-lib` — affected >=3.29.0 <3.30.30
- Maven: `org.mapfish.print:print-lib` — affected >=3.31.0 <3.31.21
- Maven: `org.mapfish.print:print-lib` — affected >=3.32.0 <3.33.14
- Maven: `org.mapfish.print:print-lib` — affected >=3.34.0 <4.0.3
- Maven: `org.mapfish.print:print-servlet` — affected >=3.23.0 <3.28.28
- Maven: `org.mapfish.print:print-servlet` — affected >=3.29.0 <3.30.30
- Maven: `org.mapfish.print:print-servlet` — affected >=3.31.0 <3.31.21
- Maven: `org.mapfish.print:print-servlet` — affected >=3.32.0 <3.33.14
- Maven: `org.mapfish.print:print-servlet` — affected >=3.34.0 <4.0.3

## Details
### Impact

The attacker can execute arbitrary code without being authenticated

### Mitigation

Upgrade to a patched version (please check affected/patched version matrix)

### Credits

Bug Bounty of Canton du Jura

## References
- https://github.com/mapfish/mapfish-print/security/advisories/GHSA-q7m6-wpvf-mvwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-44672
- https://github.com/mapfish/mapfish-print
