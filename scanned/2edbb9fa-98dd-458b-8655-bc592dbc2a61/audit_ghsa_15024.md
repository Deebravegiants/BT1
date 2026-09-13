# [C] Silverpeas authentication bypass

## Summary
Severity: Critical
Advisory: GHSA-4w54-wwc9-x62c
CVE: CVE-2024-36042
CWE: CWE-288
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-03
Source: https://github.com/advisories/GHSA-4w54-wwc9-x62c
Type: github-advisory

## Affected
- Maven: `org.silverpeas.core:silverpeas-core` — affected >=0 <6.3.5

## Details
Silverpeas before 6.3.5 allows authentication bypass by omitting the Password field to AuthenticationServlet, often providing an unauthenticated user with superadmin access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36042
- https://github.com/Silverpeas/Silverpeas-Core/commit/11fb5e21c252ce4751b85fccf5b8076156e0b4f0
- https://gist.github.com/ChrisPritchard/4b6d5c70d9329ef116266a6c238dcb2d
- https://github.com/Silverpeas/Silverpeas-Core
- https://github.com/Silverpeas/Silverpeas-Core/tags
- https://silverpeas.org
