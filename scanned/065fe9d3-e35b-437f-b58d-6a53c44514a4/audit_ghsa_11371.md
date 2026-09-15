# [H] .NET Denial of Service Vulnerability

## Summary
Severity: High
Advisory: GHSA-4vgm-c2wm-63mw
CVE: CVE-2026-26130
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-4vgm-c2wm-63mw
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm64` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm64` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm64` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm64` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm64` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm64` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-x64` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-x64` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-x64` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-x64` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-x64` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-x64` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-arm64` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-arm64` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-arm64` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-x64` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-x64` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-x64` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm64` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm64` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm64` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x64` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x64` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x64` — affected >=10.0.0 <10.0.4
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x86` — affected >=8.0.0 <8.0.25
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x86` — affected >=9.0.0 <9.0.14
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x86` — affected >=10.0.0 <10.0.4

## Details
# Microsoft Security Advisory CVE-2026-26130 – .NET Denial of Service Vulnerability

## Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 8.0, .NET 9.0, and .NET 10.0. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A denial of service vulnerability exists in ASP.NET Core due to uncontrolled resource consumption. A specially crafted message to a SignalR server can exhaust an internal buffer and cause a Denial of Service.

## Announcement

Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/385

## CVSS Details

- **Version:** 3.1
- **Score:** 7.5
- **Vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/E:U/RL:O/RC:C`
- **Severity:** High
- **Weakness:** CWE-770 (Uncontrolled Resource Consumption)

## Affected Platforms

- **Platforms:** All
- **Architectures:** All

## Affected Products

### <a name=".NET 8"></a>.NET 8
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.AspNetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm)               | >= 8.0.0, < =8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm64)           | >= 8.0.0, < =8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm)     | >= 8.0.0, <= 8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm64) | >= 8.0.0, <= 8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-x64)     | >= 8.0.0, < =8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-x64)               | >= 8.0.0, < =8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-arm64)               | >= 8.0.0, < =8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-x64)                   | >= 8.0.0, <= 8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm)                   | >= 8.0.0, <= 8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm64)               | >= 8.0.0, <= 8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x64)                   | >= 8.0.0, < =8.0.24 | 8.0.25
[Microsoft.AspNetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x86)                   | >= 8.0.0, <= 8.0.24 | 8.0.25


### <a name=".NET 9"></a>.NET 9
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.AspNetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm)               | >= 9.0.0, < =9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm64)           | >= 9.0.0, < =9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm)     | >= 9.0.0, <= 9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm64) | >= 9.0.0, <= 9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-x64)     | >= 9.0.0, < =9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-x64)               | >= 9.0.0, < =9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-arm64)               | >= 9.0.0, < =9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-x64)                   | >= 9.0.0, < =9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm)                   | >= 9.0.0, <= 9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm64)               | >= 9.0.0, < =9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x64)                   | >= 9.0.0, <= 9.0.13 | 9.0.14
[Microsoft.AspNetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x86)                   | >= 9.0.0, <= 9.0.13 | 9.0.14

### <a name=".NET 10"></a>.NET 10
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.AspNetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm)               | >= 10.0.0, < =10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm64)           | >= 10.0.0, <= 10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm)     | >= 10.0.0, < =10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm64) | >= 10.0.0, < =10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-x64)     | >= 10.0.0, < =10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-x64)               | >= 10.0.0, < =10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-arm64)               | >= 10.0.0, < =10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-x64)                   | >= 10.0.0, < =10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm)                   | >= 10.0.0, < =10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm64)               | >= 10.0.0, <= 10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x64)                   | >= 10.0.0, <= 10.0.3 | 10.0.4
[Microsoft.AspNetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x86)                   | >= 10.0.0, <= 10.0.3 | 10.0.4

## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If using an affected package listed in [affected products](#affected-products) or [affected packages](#affected-packages), you're exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

1. To fix the issue please install the latest version of .NET 8.0, NET 9.0, or .NET 10.0, as appropriate. If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET  SDKs.
2. If your application references the vulnerable package, update the package reference to the patched version. You can list the versions you have installed by running the `dotnet --info` command. 

Once you have installed the updated runtime or SDK, restart your apps for the update to take effect.

Additionally, if you've deployed [self-contained applications](https://docs.microsoft.com/dotnet/core/deploying/#self-contained-deployments-scd) targeting any of the impacted versions, these applications are also vulnerable and must be recompiled and redeployed.

## Other Information

### Reporting Security Issues

If you have found a potential security issue in a supported version of .NET, please report it to the Microsoft Security Response Center (MSRC) via the [MSRC Researcher Portal](https://msrc.microsoft.com/report/vulnerability/new). Further information can be found in the MSRC [Report an Issue FAQ](https://www.microsoft.com/msrc/faqs-report-an-issue).

Security reports made through MSRC may qualify for the Microsoft .NET Bounty. Details of the Microsoft .NET Bounty Program including terms and conditions are at https://aka.ms/corebounty.

### Support

You can ask questions about this issue on GitHub in the .NET GitHub organization. The main repos are located at https://github.com/dotnet/runtime. The Announcements repo (https://github.com/dotnet/Announcements) will contain this bulletin as an issue and will include a link to a discussion issue. You can ask questions in the linked discussion issue.

### Disclaimer

The information provided in this advisory is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

### External Links

[CVE-2026-26130]( https://www.cve.org/CVERecord?id=CVE-2026-26130)

### Acknowledgements

Bartłomiej Dach

### Revisions

V1.0 (March 10, 2026): Advisory published.

## References
- https://github.com/dotnet/aspnetcore/security/advisories/GHSA-4vgm-c2wm-63mw
- https://nvd.nist.gov/vuln/detail/CVE-2026-26130
- https://github.com/dotnet/aspnetcore
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-26130
- https://www.cve.org/CVERecord?id=CVE-2026-26130
