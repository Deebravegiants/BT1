# [H] ASP.NET Core allow an elevation of privilege

## Summary
Severity: High
Advisory: GHSA-365p-96qv-xr7g
CVE: CVE-2018-0787
CWE: CWE-640
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-365p-96qv-xr7g
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.HttpOverrides` — affected >=2.0.0 <2.0.2
- NuGet: `Microsoft.AspNetCore.Server.Kestrel.Core` — affected >=2.0.0 <2.0.2

## Details
ASP.NET Core 1.0. 1.1, and 2.0 allow an elevation of privilege vulnerability due to how web applications that are created from templates validate web requests, aka "ASP.NET Core Elevation Of Privilege Vulnerability".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0787
- https://github.com/aspnet/Announcements/issues/295
- https://github.com/advisories/GHSA-365p-96qv-xr7g
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0787
- http://www.securityfocus.com/bid/103282
- http://www.securitytracker.com/id/1040525
