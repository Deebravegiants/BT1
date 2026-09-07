# [H] Eclipse GlassFish is vulnerable to Server Side Request Forgery attacks through specific endpoints

## Summary
Severity: High
Advisory: GHSA-f7h5-c625-3795
CVE: CVE-2024-9408
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2025-07-16
Source: https://github.com/advisories/GHSA-f7h5-c625-3795
Type: github-advisory

## Affected
- Maven: `org.glassfish.main.admingui:console-common` — affected >=0

## Details
In Eclipse GlassFish version 6.2.5, it is possible to perform a Server Side Request Forgery attack using specific endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9408
- https://github.com/eclipse-ee4j/glassfish
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/38
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/239
