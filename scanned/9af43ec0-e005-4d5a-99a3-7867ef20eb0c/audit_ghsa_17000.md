# [H] Eclipse Kura LogServlet vulnerability

## Summary
Severity: High
Advisory: GHSA-frc2-w2cc-x794
CVE: CVE-2024-3046
CWE: CWE-303
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-frc2-w2cc-x794
Type: github-advisory

## Affected
- Maven: `org.eclipse.kura:org.eclipse.kura.web2` — affected >=2.0.600

## Details
In Eclipse Kura LogServlet component included in versions 5.0.0 to 5.4.1, a specifically crafted request to the servlet can allow an unauthenticated user to retrieve the device logs. Also, downloaded logs may be used by an attacker to perform privilege escalation by using the session id of an authenticated user reported in logs.

This issue affects org.eclipse.kura:org.eclipse.kura.web2 version range [2.0.600, 2.4.0], which is included in Eclipse Kura version range [5.0.0, 5.4.1].

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3046
- https://github.com/eclipse/kura
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/188
