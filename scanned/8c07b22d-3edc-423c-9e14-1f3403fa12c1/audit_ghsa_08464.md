# [C] GlassFish's Administration Console is Vulnerable to RCE

## Summary
Severity: Critical
Advisory: GHSA-96v6-hq43-x9h4
CVE: CVE-2026-2586
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-96v6-hq43-x9h4
Type: github-advisory

## Affected
- Maven: `org.glassfish.main.admingui:console-common` — affected >=0 <8.0.2
- Maven: `org.glassfish.jsftemplating:jsftemplating` — affected >=0 <4.2.0

## Details
An authenticated Remote Code Execution (RCE) vulnerability was identified in GlassFish's Administration Console. A user with access to the panel can send crafted requests that allow the execution of arbitrary operating system commands with the privileges of the application service user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2586
- https://github.com/eclipse-ee4j/glassfish
- https://github.com/eclipse-ee4j/glassfish/releases/tag/8.0.2
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/87
