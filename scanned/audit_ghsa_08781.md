# [C] GlassFish's gadget handler is vulnerable to RCE

## Summary
Severity: Critical
Advisory: GHSA-29wv-cv7p-xjc2
CVE: CVE-2026-2587
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-29wv-cv7p-xjc2
Type: github-advisory

## Affected
- Maven: `org.glassfish.main.admingui:admingui` — affected >=0 <8.0.2
- Maven: `org.glassfish.jsftemplating:jsftemplating` — affected >=0 <4.2.0

## Details
A critical Remote Code Execution (RCE) vulnerability was identified in the server-side template rendering mechanism used by the Glassfish gadget handler. The application processes .xml files and evaluates user-supplied values within a context where Expression Language (EL) “expressions” are processed without proper sanitization or escaping. By injecting expressions such as #{7*7}, the server returns 49, confirming server-side EL evaluation. This issue allows a remote attacker to fully compromise the underlying host, enabling capabilities as reading/modifying data, executing arbitrary commands, persistence, and lateral movement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2587
- https://github.com/eclipse-ee4j/glassfish
- https://github.com/eclipse-ee4j/glassfish/releases/tag/8.0.2
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/86
