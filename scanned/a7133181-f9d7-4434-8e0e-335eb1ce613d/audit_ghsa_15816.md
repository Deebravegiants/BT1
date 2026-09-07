# [M] Umbraco CMS logout page displayed before session expiration

## Summary
Severity: Medium
Advisory: GHSA-fp6q-gccw-7qqm
CVE: CVE-2024-48926
CWE: CWE-613
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-22
Source: https://github.com/advisories/GHSA-fp6q-gccw-7qqm
Type: github-advisory

## Affected
- NuGet: `Umbraco.CMS` — affected >=13.0.0 <13.5.2
- NuGet: `Umbraco.CMS` — affected >=10.0.0 <10.8.7
- NuGet: `UmbracoCMS` — affected >=8.0.0 <8.18.15

## Details
### Impact
The Backoffice displays the logout page with a session timeout message before the server session has fully expired, causing users to believe they have been logged out approximately 30 seconds before they actually are.

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-fp6q-gccw-7qqm
- https://nvd.nist.gov/vuln/detail/CVE-2024-48926
- https://github.com/umbraco/Umbraco-CMS
