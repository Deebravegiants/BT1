# [M] Moderate severity vulnerability that affects Microsoft.AspNetCore.All, Microsoft.AspNetCore.App, and Microsoft.AspNetCore.Server.Kestrel.Core

## Summary
Severity: Medium
Advisory: GHSA-cgpw-2gph-2r9g
Ecosystem: NuGet
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-cgpw-2gph-2r9g
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.Server.Kestrel.Core` — affected >=2.0.0 <2.0.4
- NuGet: `Microsoft.AspNetCore.All` — affected >=2.0.0 <2.0.9
- NuGet: `Microsoft.AspNetCore.App` — affected >=2.1.0 <2.1.2
- NuGet: `Microsoft.AspNetCore.Server.Kestrel.Core` — affected >=2.1.0 <2.1.2
- NuGet: `Microsoft.AspNetCore.All` — affected >=2.1.0 <2.1.2

## Details
Microsoft is aware of a denial of service vulnerability in ASP.NET Core when a malformed request is terminated. An attacker who successfully exploited this vulnerability could cause a denial of service attack.

The update addresses the vulnerability by correcting how ASP.NET Core handles such requests.

## References
- https://github.com/aspnet/Announcements/issues/311
- https://github.com/advisories/GHSA-cgpw-2gph-2r9g
