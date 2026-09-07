# [M] Eclipse GlassFish is vulnerable to Stored XSS attacks through configuration file modifications

## Summary
Severity: Medium
Advisory: GHSA-hp97-5x6g-q538
CVE: CVE-2024-10031
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:H/AT:N/PR:H/UI:P/VC:L/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2025-07-16
Source: https://github.com/advisories/GHSA-hp97-5x6g-q538
Type: github-advisory

## Affected
- Maven: `org.glassfish.main.admingui:console-common` — affected >=0

## Details
In Eclipse GlassFish version 7.0.15 is possible to perform Stored Cross-site Scripting attacks by modifying the configuration file in the underlying operating system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10031
- https://github.com/eclipse-ee4j/glassfish
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/41
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/229
