# [H] Remote code execution in ASP.NET Core

## Summary
Severity: High
Advisory: GHSA-655q-9gvg-q4cm
CVE: CVE-2020-0603
CWE: CWE-119
Ecosystem: NuGet
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-655q-9gvg-q4cm
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.All` — affected >=2.1.0 <2.1.15
- NuGet: `Microsoft.AspNetCore.App` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.AspNetCore.App` — affected >=3.0.0 <3.0.1
- NuGet: `Microsoft.AspNetCore.App` — affected >=2.1.0 <2.1.15
- NuGet: `Microsoft.AspNetCore.Http.Connections` — affected >=1.0.0 <1.0.15
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm64` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm64` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-x64` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-x64` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-x64` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x64` — affected >=3.1.0 <3.1.1
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x86` — affected >=3.1.0 <3.1.1

## Details
A remote code execution vulnerability exists in ASP.NET Core software when the software fails to handle objects in memory.An attacker who successfully exploited the vulnerability could run arbitrary code in the context of the current user, aka 'ASP.NET Core Remote Code Execution Vulnerability'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-0603
- https://github.com/aspnet/Announcements/issues/403
- https://github.com/github/advisory-database/issues/302
- https://access.redhat.com/errata/RHSA-2020:0130
- https://access.redhat.com/errata/RHSA-2020:0134
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0603
