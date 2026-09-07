# [M] Silverpeas Core has a reflected cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vmj7-7xmm-4349
CVE: CVE-2026-30139
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-vmj7-7xmm-4349
Type: github-advisory

## Affected
- Maven: `org.silverpeas.core:silverpeas-core-war` — affected >=0
- Maven: `org.silverpeas.core:silverpeas-core-web` — affected >=0

## Details
A reflected cross-site scripting (XSS) vulnerability in the AdvancedSearch functionality of Silverpeas Core allows attackers to execute arbitrary JavaScript in the context of a user's browser via crafted input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-30139
- https://github.com/Silverpeas/Silverpeas-Core/pull/1421
- https://github.com/Silverpeas/Silverpeas-Core/commit/7b4bacc80d11ab60423bdc6eb69e0176e9c27fc7
- https://github.com/Silverpeas/Silverpeas-Core
- https://github.com/bodd1593/CVEs-huyle/tree/main/CVE-2026-30139
