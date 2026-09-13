# [H] .NET Core & .NET Framework Denial of Service Vulnerability

## Summary
Severity: High
Advisory: GHSA-3w5p-jhp5-c29q
CVE: CVE-2020-1108
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3w5p-jhp5-c29q
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App` — affected >=2.1.0 <2.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.rhel.6-x64` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm64` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=3.1.0 <3.1.4
- NuGet: `Microsoft.NETCore.App.Runtime.win-x86` — affected >=3.1.0 <3.1.4

## Details
A denial of service vulnerability exists when .NET Core or .NET Framework improperly handles web requests, aka '.NET Core & .NET Framework Denial of Service Vulnerability'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1108
- https://github.com/dotnet/announcements/issues/157
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1108
