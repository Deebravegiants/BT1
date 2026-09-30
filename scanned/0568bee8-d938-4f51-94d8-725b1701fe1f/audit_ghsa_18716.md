# [M] Microsoft Security Advisory CVE-2025-55248: .NET Information Disclosure Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gwq6-fmvp-qp68
CVE: CVE-2025-55248
CWE: CWE-326
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-gwq6-fmvp-qp68
Type: github-advisory

## Affected
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-x64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-x64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.osx-arm64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.osx-x64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.win-x64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.win-x86` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-x64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.linux-x64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.osx-arm64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.osx-x64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.win-x64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.NetCore.App.Runtime.win-x86` — affected >=8.0.0 <8.0.21

## Details
# Microsoft Security Advisory CVE-2025-55248 | .NET Information Disclosure Vulnerability

## <a name="executive-summary"></a>Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 8.0 and .NET 9.0. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A MITM (man in the middle) attacker may prevent use of TLS between client and SMTP server, forcing client to send data over unencrypted connection.

## Announcement

Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/372

## <a name="mitigation-factors"></a>Mitigation factors

Microsoft has not identified any mitigating factors for this vulnerability.

## <a name="affected-software"></a>Affected software

* Any .NET 8.0 application running on .NET 8.0.20 or earlier.
* Any .NET 9.0 application running on .NET 9.0.9 or earlier.

## <a name="affected-packages"></a>Affected Packages
The vulnerability affects any Microsoft .NET project if it uses any of affected packages versions listed below

### <a name=".NET 9"></a>.NET 9
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm)               | >= 9.0.0, < =9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm64)           | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm)     | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm64) | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-x64)     | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-x64)               | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-arm64)               | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-x64)                   | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm)                   | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm64)               | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x64)                   | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.NetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x86)                   | >= 9.0.0, <= 9.0.9 | 9.0.10

### <a name=".NET 8"></a>.NET 8
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm)               | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm64)           | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm)     | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm64) | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-x64)     | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-x64)               | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-arm64)               | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-x64)                   | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm)                   | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm64)               | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x64)                   | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.NetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x86)                   | >= 8.0.0, <= 8.0.20 | 8.0.21

## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If you have a runtime with a version listed, or an affected package listed in [affected software](#affected-packages) or [affected packages](#affected-software), you're exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

1. To fix the issue please install the latest version of .NET 9.0 or .NET 8.0, as appropriate. If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET  SDKs.
2. If your application references the vulnerable package, update the package reference to the patched version.

* You can list the versions you have installed by running the `dotnet --info` command. You will see output like the following;

```
.NET SDK:
 Version:           9.0.100
 Commit:            59db016f11
 Workload version:  9.0.100-manifests.3068a692
 MSBuild version:   17.12.7+5b8665660

Runtime Environment:
 OS Name:     Mac OS X
 OS Version:  15.2
 OS Platform: Darwin
 RID:         osx-arm64
 Base Path:   /usr/local/share/dotnet/sdk/9.0.100/

.NET workloads installed:
There are no installed workloads to display.
Configured to use loose manifests when installing new manifests.

Host:
  Version:      9.0.0
  Architecture: arm64
  Commit:       9d5a6a9aa4

.NET SDKs installed:
  9.0.100 [/usr/local/share/dotnet/sdk]

.NET runtimes installed:
  Microsoft.AspNetCore.App 9.0.0 [/usr/local/share/dotnet/shared/Microsoft.AspNetCore.App]
  Microsoft.NETCore.App 9.0.0 [/usr/local/share/dotnet/shared/Microsoft.NETCore.App]

Other architectures found:
  x64   [/usr/local/share/dotnet]
    registered at [/etc/dotnet/install_location_x64]

Environment variables:
  Not set

global.json file:
  Not found

Learn more:
  https://aka.ms/dotnet/info

Download .NET:
  https://aka.ms/dotnet/download
```

* If you're using .NET 8.0, you should download and install .NET 8.0.21  Runtime or .NET 8.0.318 SDK (for Visual Studio 2022 v17.10 latest update) from https://dotnet.microsoft.com/download/dotnet-core/8.0.
* If you're using .NET 9.0, you should download and install .NET 9.0.10  Runtime or .NET 9.0.111 SDK (for Visual Studio 2022 v17.12 latest update) from https://dotnet.microsoft.com/download/dotnet-core/9.0.

Once you have installed the updated runtime or SDK, restart your apps for the update to take effect.

Additionally, if you've deployed [self-contained applications](https://docs.microsoft.com/dotnet/core/deploying/#self-contained-deployments-scd) targeting any of the impacted versions, these applications are also vulnerable and must be recompiled and redeployed.

## Other Information

### Reporting Security Issues

If you have found a potential security issue in .NET 9.0 or .NET 8.0, please email details to secure@microsoft.com. Reports may qualify for the Microsoft .NET Core & .NET 5 Bounty. Details of the Microsoft .NET Bounty Program including terms and conditions are at <https://aka.ms/corebounty>.

### Support

You can ask questions about this issue on GitHub in the .NET GitHub organization. The main repos are located at https://github.com/dotnet/runtime. The Announcements repo (https://github.com/dotnet/Announcements) will contain this bulletin as an issue and will include a link to a discussion issue. You can ask questions in the linked discussion issue.

### Disclaimer

The information provided in this advisory is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

### External Links

[CVE-2025-55248]( https://www.cve.org/CVERecord?id=CVE-2025-55248)

### Revisions

V1.0 (October 14, 2025): Advisory published.

## References
- https://github.com/dotnet/runtime/security/advisories/GHSA-gwq6-fmvp-qp68
- https://github.com/dotnet/announcements/issues/372
- https://github.com/dotnet/runtime/issues/120713
- https://github.com/dotnet/runtime
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-55248
