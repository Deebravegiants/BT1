# [M] Eclipse GlassFish is vulnerable to Reflected XSS attacks through its Administration Console

## Summary
Severity: Medium
Advisory: GHSA-vqrm-83g6-pfv4
CVE: CVE-2024-10029
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:A/VC:L/VI:L/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2025-07-16
Source: https://github.com/advisories/GHSA-vqrm-83g6-pfv4
Type: github-advisory

## Affected
- Maven: `org.glassfish.main.admingui:console-common` — affected >=0
- Maven: `org.glassfish.main.admingui:console-cluster-plugin` — affected >=0

## Details
In Eclipse GlassFish version 7.0.15, it is possible to perform Reflected Cross-Site Scripting attacks through the Administration Console.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10029
- https://github.com/eclipse-ee4j/glassfish
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/40
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/226
