# [M] Silverpeas Core Username Enumeration Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cv2m-5pfp-f245
CVE: CVE-2025-46047
CWE: CWE-204
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-02
Source: https://github.com/advisories/GHSA-cv2m-5pfp-f245
Type: github-advisory

## Affected
- Maven: `org.silverpeas.core:silverpeas-core` — affected >=6.4.1 <6.4.3

## Details
A User enumeration vulnerability in the /CredentialsServlet/ForgotPassword endpoint in Silverpeas 6.4.1 and 6.4.2 allows remote attackers to determine valid usernames via the Login parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-46047
- https://github.com/Silverpeas/Silverpeas-Core/pull/1399
- https://github.com/Silverpeas/Silverpeas-Core/commit/c283ce13d81ba7abf6adcd226338c95c5875a398
- https://github.com/J0ey17/Silverpeas-Username-Enumeration-PoC
- https://github.com/Silverpeas/Silverpeas-Core
