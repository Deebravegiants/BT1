# [H] Eclipse Jetty: Early return from the JASPIAuthenticator code can potentially no clear ThreadLocal variables

## Summary
Severity: High
Advisory: GHSA-r7p8-xq5m-436c
CVE: CVE-2026-5795
CWE: CWE-226, CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-r7p8-xq5m-436c
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty.ee11:jetty-ee11-jaspi` — affected >=12.1.0 <12.1.8
- Maven: `org.eclipse.jetty.ee10:jetty-ee10-jaspi` — affected >=12.1.0 <12.1.8
- Maven: `org.eclipse.jetty.ee9:jetty-ee9-jaspi` — affected >=12.1.0 <12.1.8
- Maven: `org.eclipse.jetty.ee8:jetty-ee8-jaspi` — affected >=12.1.0 <12.1.8
- Maven: `org.eclipse.jetty.ee11:jetty-ee11-jaspi` — affected >=12.0.0 <12.0.34
- Maven: `org.eclipse.jetty.ee10:jetty-ee10-jaspi` — affected >=12.0.0 <12.0.34
- Maven: `org.eclipse.jetty.ee9:jetty-ee9-jaspi` — affected >=12.0.0 <12.0.34
- Maven: `org.eclipse.jetty.ee8:jetty-ee8-jaspi` — affected >=12.0.0 <12.0.34
- Maven: `org.eclipse.jetty:jetty-jaspi` — affected >=11.0.0 <11.0.29
- Maven: `org.eclipse.jetty:jetty-jaspi` — affected >=10.0.0 <10.0.29
- Maven: `org.eclipse.jetty:jetty-jaspi` — affected >=9.4.0 <9.4.61

## Details
### Description (as reported)

A security vulnerability has been identified in Jetty's  `JaspiAuthenticator.java`. 

The root cause is a failure to consistently clear authentication metadata stored in  `ThreadLocal`  during certain error or incomplete authentication flows. 
Specifically, after a `GroupPrincipalCallback`  is persisted into the  `ThreadLocal`, the authentication process may exit prematurely — before the  `ThreadLocal`  storage is cleared — if a mandatory `CallerPrincipalCallback`  is missing or an exception occurs. 
This allows a subsequent, unprivileged user processed by the same worker thread to inherit these residual security roles, leading to Broken Access Control and Privilege Escalation.

See also attached PDF.

### Impact
An unauthenticated user may gain ungrated privileges from a previous request (privilege escalation).

### Patches
No patches yet.

### Workarounds
Do not use Jetty's JASPI.

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-r7p8-xq5m-436c
- https://nvd.nist.gov/vuln/detail/CVE-2026-5795
- https://github.com/jetty/jetty.project
- https://github.com/user-attachments/files/26118760/JaspiAuthenticator_Security_Report.pdf
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/92
