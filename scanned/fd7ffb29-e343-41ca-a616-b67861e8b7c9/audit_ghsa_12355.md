# [H] Cross Site Request Forgery in Silverpeas

## Summary
Severity: High
Advisory: GHSA-g27c-w2v7-88xp
CVE: CVE-2023-47322
CWE: CWE-352, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-g27c-w2v7-88xp
Type: github-advisory

## Affected
- Maven: `org.silverpeas.core:silverpeas-core-web` — affected >=0 <6.3.2

## Details
The "userModify" feature of Silverpeas Core 6.3.1 is vulnerable to Cross Site Request Forgery (CSRF) leading to privilege escalation. If an administrator goes to a malicious URL while being authenticated to the Silverpeas application, the CSRF with execute making the attacker an administrator user in the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47322
- https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2023-47322
- https://github.com/Silverpeas/Silverpeas-Core
- http://silverpeas.com
