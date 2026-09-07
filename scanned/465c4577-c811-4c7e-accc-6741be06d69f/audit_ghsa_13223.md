# [M] Microsoft Security Advisory CVE-2023-36799: .NET Denial of Service Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h3hv-63q5-jgpr
CVE: CVE-2023-36799
CWE: CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-12
Source: https://github.com/advisories/GHSA-h3hv-63q5-jgpr
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=7.0.0 <7.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=7.0.0 <7.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=7.0.0 <7.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm` — affected >=7.0.0 <7.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=7.0.0 <7.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=7.0.0 <7.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=6.0.0 <6.0.22
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=6.0.0 <6.0.22
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm` — affected >=6.0.0 <6.0.22
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=6.0.0 <6.0.22
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=6.0.0 <6.0.22
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=6.0.0 <6.0.22

## Details
# Microsoft Security Advisory CVE-2023-36799: .NET Denial of Service Vulnerability

## <a name="executive-summary"></a>Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 7.0 and .NET 6.0. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A vulnerability exists in .NET where reading a maliciously crafted X.509 certificate may result in Denial of Service. This issue only affects Linux systems.

## Announcement

Announcement for this issue can be found at  https://github.com/dotnet/announcements/issues/275

### <a name="mitigation-factors"></a>Mitigation factors

Microsoft has not identified any mitigating factors for this vulnerability.

## <a name="affected-software"></a>Affected software

* Any .NET 7.0 application running on .NET 7.0.10 or earlier.
* Any .NET 6.0 application running on .NET 6.0.21 or earlier.

If your application uses the following package versions, ensure you update to the latest version of .NET.

### <a name=".NET 7"></a>.NET 7

Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NETCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm64) | >= 7.0.0, <= 7.0.10 | 7.0.11
[Microsoft.NETCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm64) | >= 7.0.0, <= 7.0.10 | 7.0.11
[Microsoft.NETCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm) | >= 7.0.0, <= 7.0.10 | 7.0.11
[Microsoft.NETCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm) | >= 7.0.0, <= 7.0.10 | 7.0.11
[Microsoft.NETCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-x64) | >= 7.0.0, <= 7.0.10 | 7.0.11
[Microsoft.NETCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-x64) | >= 7.0.0, <= 7.0.10 | 7.0.11


### <a name=".NET 6"></a>.NET 6

Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NETCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm64) | >= 6.0.0, <= 6.0.21 | 6.0.22
[Microsoft.NETCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm64) | >= 6.0.0, <= 6.0.21 | 6.0.22
[Microsoft.NETCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm) | >= 6.0.0, <= 6.0.21 | 6.0.22
[Microsoft.NETCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm) | >= 6.0.0, <= 6.0.21 | 6.0.22
[Microsoft.NETCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-x64) | >= 6.0.0, <= 6.0.21 | 6.0.22
[Microsoft.NETCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-x64) | >= 6.0.0, <= 6.0.21 | 6.0.22


## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If you have a runtime or SDK with a version listed, or an affected package listed in [affected software](#affected-software), you're exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

* To fix the issue please install the latest version of .NET 6.0 or .NET 7.0. If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET  SDKs.
* If you are using one of the affected packages, please update to the patched version listed above.
* If you have .NET 6.0 or greater installed, you can list the versions you have installed by running the `dotnet --info` command. You will see output like the following;

```
.NET Core SDK (reflecting any global.json):

 Version:   6.0.300
 Commit:    8473146e7d

Runtime Environment:

 OS Name:     Windows
 OS Version:  10.0.18363
 OS Platform: Windows
 RID:         win10-x64
 Base Path:   C:\Program Files\dotnet\sdk\6.0.300\

Host (useful for support):

  Version: 6.0.5
  Commit:  8473146e7d

.NET Core SDKs installed:

  6.0.300 [C:\Program Files\dotnet\sdk]

.NET Core runtimes installed:

  Microsoft.AspNetCore.App 6.0.5 [C:\Program Files\dotnet\shared\Microsoft.AspNetCore.App]
  Microsoft.NETCore.App 6.0.5 [C:\Program Files\dotnet\shared\Microsoft.NETCore.App]
  Microsoft.WindowsDesktop.App 6.0.5 [C:\Program Files\dotnet\shared\Microsoft.WindowsDesktop.App]

To install additional .NET Core runtimes or SDKs:
  https://aka.ms/dotnet-download
```

* If you're using .NET 7.0, you should download and install Runtime 7.0.11 or SDK 7.0.111 (for Visual Studio 2022 v17.4) from https://dotnet.microsoft.com/download/dotnet-core/7.0.
* If you're using .NET 6.0, you should download and install Runtime 6.0.22 or SDK 6.0.317 (for Visual Studio 2022 v17.2) from https://dotnet.microsoft.com/download/dotnet-core/6.0.

.NET 6.0 and and .NET 7.0 updates are also available from Microsoft Update. To access this either type "Check for updates" in your Windows search, or open Settings, choose Update & Security and then click Check for Updates.

Once you have installed the updated runtime or SDK, restart your apps for the update to take effect.

Additionally, if you've deployed [self-contained applications](https://docs.microsoft.com/dotnet/core/deploying/#self-contained-deployments-scd) targeting any of the impacted versions, these applications are also vulnerable and must be recompiled and redeployed.

## Other Information

### Reporting Security Issues

If you have found a potential security issue in .NET 6.0 or .NET 7.0, please email details to secure@microsoft.com. Reports may qualify for the Microsoft .NET Core & .NET 5 Bounty. Details of the Microsoft .NET Bounty Program including terms and conditions are at <https://aka.ms/corebounty>.

### Support

You can ask questions about this issue on GitHub in the .NET GitHub organization. The main repos are located at https://github.com/dotnet/runtime and https://github.com/dotnet/aspnet/. The Announcements repo (https://github.com/dotnet/Announcements) will contain this bulletin as an issue and will include a link to a discussion issue. You can ask questions in the linked discussion issue.

### Disclaimer

The information provided in this advisory is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

### External Links

[CVE-2023-36799]( https://www.cve.org/CVERecord?id=CVE-2023-36799)

### Revisions

V1.0 (September 12, 2023): Advisory published.

_Version 1.0_

_Last Updated 2023-09-12_

## References
- https://github.com/dotnet/runtime/security/advisories/GHSA-h3hv-63q5-jgpr
- https://nvd.nist.gov/vuln/detail/CVE-2023-36799
- https://github.com/dotnet/runtime
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-36799
