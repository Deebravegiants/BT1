# [M] Eclipse GlassFish is vulnerable to Login Brute Force attacks through unlimited failed login attempts

## Summary
Severity: Medium
Advisory: GHSA-99f7-hp6j-v6q4
CVE: CVE-2024-9342
CWE: CWE-307
Ecosystem: Maven
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-07-16
Source: https://github.com/advisories/GHSA-99f7-hp6j-v6q4
Type: github-advisory

## Affected
- Maven: `org.glassfish.main.admingui:console-common` — affected >=0

## Details
In Eclipse GlassFish version 7.0.16 or earlier, it is possible to perform login brute force attacks as there is no limitation on the number of failed login attempts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9342
- https://github.com/eclipse-ee4j/glassfish
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/33
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/231
