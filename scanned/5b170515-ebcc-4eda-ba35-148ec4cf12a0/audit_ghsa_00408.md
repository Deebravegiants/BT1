# [H] Security feature bypass vulnerability exists in ASP.NET when the number of incorrect login attempts is not validated

## Summary
Severity: High
Advisory: GHSA-vhvh-528q-ff3p
CVE: CVE-2018-8171
CWE: CWE-287
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-vhvh-528q-ff3p
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.Identity` — affected >=1.0.0 <1.0.6
- NuGet: `Microsoft.AspNetCore.Identity` — affected >=1.1.0 <1.1.6
- NuGet: `Microsoft.AspNetCore.Identity` — affected >=2.0.0 <2.0.4
- NuGet: `Microsoft.AspNetCore.Identity` — affected >=2.1.0 <2.1.2

## Details
A Security Feature Bypass vulnerability exists in ASP.NET when the number of incorrect login attempts is not validated, aka "ASP.NET Security Feature Bypass Vulnerability." This affects ASP.NET, ASP.NET Core 1.1, ASP.NET Core 1.0, ASP.NET Core 2.0, ASP.NET MVC 5.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8171
- https://github.com/advisories/GHSA-vhvh-528q-ff3p
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8171
- http://www.securityfocus.com/bid/104659
- http://www.securitytracker.com/id/1041267
