# [H] Cookie parsing failure

## Summary
Severity: High
Advisory: GHSA-hxrm-9w7p-39cc
CVE: CVE-2020-1045
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hxrm-9w7p-39cc
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.Http` — affected >=0 <2.1.22
- NuGet: `Microsoft.AspNetCore.App` — affected >=0 <2.1.22
- NuGet: `Microsoft.Owin` — affected >=0 <4.1.1
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm` — affected >=3.1.0 <3.1.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm64` — affected >=3.1.0 <3.1.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-x64` — affected >=3.1.0 <3.1.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-x64` — affected >=3.1.0 <3.1.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-x64` — affected >=3.1.0 <3.1.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm` — affected >=3.1.0 <3.1.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x64` — affected >=3.1.0 <3.1.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x86` — affected >=3.1.0 <3.1.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm64` — affected >=3.1.0 <3.1.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm64` — affected >=3.1.5 <3.1.8

## Details
A security feature bypass vulnerability exists in the way Microsoft ASP.NET Core parses encoded cookie names.The ASP.NET Core cookie parser decodes entire cookie strings which could allow a malicious attacker to set a second cookie with the name being percent encoded.The security update addresses the vulnerability by fixing the way the ASP.NET Core cookie parser handles encoded names., aka 'Microsoft ASP.NET Core Security Feature Bypass Vulnerability'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1045
- https://github.com/dotnet/announcements/issues/165
- https://github.com/dotnet/aspnetcore/issues/25701
- https://github.com/dotnet/aspnetcore/issues/25701#issuecomment-689434477
- https://github.com/github/advisory-database/issues/302
- https://github.com/dotnet/aspnetcore/pull/24264
- https://access.redhat.com/errata/RHSA-2020:3699
- https://github.com/dotnet/core/blob/main/release-notes/3.1/3.1.8/3.1.8.md#changes-in-318
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5LN2FUVBSVPGK7AU3NMLO3YR6CGONQPB
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ASICXQXS4M7MTAF6SGQMCLCA63DLCUT3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5LN2FUVBSVPGK7AU3NMLO3YR6CGONQPB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ASICXQXS4M7MTAF6SGQMCLCA63DLCUT3
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1045
- https://security.snyk.io/vuln/SNYK-RHEL8-DOTNET-1439600
