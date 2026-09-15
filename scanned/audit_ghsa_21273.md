# [H] .NET Core Elevation of Privilege Vulnerability

## Summary
Severity: High
Advisory: GHSA-rh58-r7jh-xhx3
CVE: CVE-2021-26423
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-rh58-r7jh-xhx3
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App.Runtime.win-x86` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.win-x86` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm64` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.osx-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.osx-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.linux-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.linux-arm64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.osx-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.linux-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.linux-arm64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-musl-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-arm64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-arm` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.rhel.6-x64` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=5.0.0 <5.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=3.1.0 <3.1.18
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=5.0.0 <5.0.9

## Details
Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 5.0 and .NET Core 3.1. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A denial of service vulnerability exists in .NET 5.0, .NET Core 3.1 and .NET Core 2.1 where .NET (Core) server applications providing WebSocket endpoints could be tricked into endlessly looping while trying to read a single WebSocket frame. 

### Patches

* If you're using .NET 5.0, you should download and install Runtime 5.0.9 or SDK 5.0.206 (for Visual Studio 2019 v16.8) or SDK 5.0.303 (for Visual Studio 2019 V16.10) from https://dotnet.microsoft.com/download/dotnet-core/5.0.

* If you're using .NET Core 3.1, you should download and install Runtime 3.1.18 or SDK 3.1.118 (for Visual Studio 2019 v16.4) or 3.1.412 (for Visual Studio 2019 v16.7 or later) from https://dotnet.microsoft.com/download/dotnet-core/3.1.

* If you're using .NET Core 2.1, you should download and install Runtime 2.1.29 or SDK 2.1.525 (for Visual Studio 2019 v15.9) or 2.1.817 from https://dotnet.microsoft.com/download/dotnet-core/2.1.


#### Other Details

- Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/194
- An Issue for this can be found at https://github.com/dotnet/runtime/issues/57175
- MSRC details for this can be found at https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-26423

## References
- https://github.com/dotnet/runtime/security/advisories/GHSA-rh58-r7jh-xhx3
- https://nvd.nist.gov/vuln/detail/CVE-2021-26423
- https://github.com/dotnet/announcements/issues/194
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2021-26423
