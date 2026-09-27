# [H] Cross-origin Resource Sharing bypass in ASP.NET Core

## Summary
Severity: High
Advisory: GHSA-3rp6-rjw4-cq39
CVE: CVE-2017-8700
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3rp6-rjw4-cq39
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.Mvc.Core` — affected >=1.0.0 <1.0.6
- NuGet: `Microsoft.AspNetCore.Mvc.Core` — affected >=1.1.0 <1.1.6
- NuGet: `Microsoft.AspNetCore.Mvc.Cors` — affected >=1.0.0 <1.0.6
- NuGet: `Microsoft.AspNetCore.Mvc.Cors` — affected >=1.1.0 <1.1.6

## Details
ASP.NET Core 1.0, 1.1, and 2.0 allow an attacker to bypass Cross-origin Resource Sharing (CORS) configurations and retrieve normally restricted content from a web application, aka "ASP.NET Core Information Disclosure Vulnerability".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8700
- https://github.com/aspnet/Announcements/issues/279
- https://github.com/github/advisory-database/issues/302
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-8700
