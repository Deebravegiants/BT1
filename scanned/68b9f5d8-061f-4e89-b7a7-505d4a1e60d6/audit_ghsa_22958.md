# [M] Denial of service in .NET core

## Summary
Severity: Medium
Advisory: GHSA-3gp9-h8hw-pxpw
CVE: CVE-2021-1721
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3gp9-h8hw-pxpw
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App` — affected >=2.1.0 <2.1.25
- NuGet: `Microsoft.NETCore.App.Host.linux-arm` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.linux-arm64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.linux-musl-arm64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.linux-musl-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.linux-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.osx-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.rhel.6-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.win-arm` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.win-arm64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.win-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Host.win-x86` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.rhel.6-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.win-x86` — affected >=3.1.0 <3.1.12
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.linux-arm64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.linux-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.osx-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.linux-arm64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.linux-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.osx-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-arm` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-arm64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-musl-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.osx-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.android-arm` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.android-arm64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.android-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.android-x86` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.browser-wasm` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.ios-arm` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.ios-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.ios-x86` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.tvos-arm64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.tvos-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=5.0.0 <5.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.win-x86` — affected >=5.0.0 <5.0.3

## Details
.NET Core and Visual Studio Denial of Service Vulnerability due to a vulnerability which exists when creating HTTPS web request during X509 certificate chain building.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-1721
- https://github.com/dotnet/announcements/issues/175
- https://github.com/dotnet/runtime/issues/48067
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2021-1721
