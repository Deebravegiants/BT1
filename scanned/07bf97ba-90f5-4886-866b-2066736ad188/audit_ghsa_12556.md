# [H] .NET Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-jh2h-qcrw-ghg7
CVE: CVE-2023-24895
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-jh2h-qcrw-ghg7
Type: github-advisory

## Affected
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-arm64` — affected >=7.0.0 <7.0.7
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x64` — affected >=7.0.0 <7.0.7
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x86` — affected >=7.0.0 <7.0.7
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-arm64` — affected >=6.0.0 <6.0.18
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x64` — affected >=6.0.0 <6.0.18
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x86` — affected >=6.0.0 <6.0.18

## Details
# Microsoft Security Advisory CVE-2023-24895: .NET Remote Code Execution Vulnerability

## <a name="executive-summary"></a>Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 7.0 and .NET 6.0. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A vulnerability exists in how WPF applications load and render XPS documents which may result in remote code execution.

## Announcement 

Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/261

### <a name="mitigation-factors"></a>Mitigation factors

Microsoft has not identified any mitigating factors for this vulnerability.

## <a name="affected-software"></a>Affected software

* Any .NET 7.0 application running on .NET 7.0.5 or earlier.
* Any .NET 6.0 application running on .NET 6.0.16 or earlier.

If your application uses the following package versions, ensure you update to the latest version of .NET.

### <a name=".NET 7"></a>.NET 7

Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.WindowsDesktop.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-arm64)      | >= 7.0.0, <= 7.0.5 | 7.0.7
[Microsoft.WindowsDesktop.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x64)          | >= 7.0.0, <= 7.0.5 | 7.0.7
[Microsoft.WindowsDesktop.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x86)          | >= 7.0.0, <= 7.0.5 | 7.0.7

### <a name=".NET 6"></a>.NET 6

Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.WindowsDesktop.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-arm64)      | >= 6.0.0, <= 6.0.16 | 6.0.18
[Microsoft.WindowsDesktop.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x64)          | >= 6.0.0, <= 6.0.16 | 6.0.18
[Microsoft.WindowsDesktop.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x86)          | >= 6.0.0, <= 6.0.16 | 6.0.18

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

* If you're using .NET 7.0, you should download and install Runtime 7.0.7 or SDK 7.0.106 (for Visual Studio 2022 v17.4) from https://dotnet.microsoft.com/download/dotnet-core/7.0.
* If you're using .NET 6.0, you should download and install Runtime 6.0.18 or SDK 6.0.312 (for Visual Studio 2022 v17.2) from https://dotnet.microsoft.com/download/dotnet-core/6.0.

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

[CVE-2023-24895]( https://www.cve.org/CVERecord?id=2023-24895)

### Revisions

V1.0 (June 13, 2023): Advisory published.

_Version 1.0_

_Last Updated 2023-05-09_

## References
- https://github.com/dotnet/wpf/security/advisories/GHSA-jh2h-qcrw-ghg7
- https://nvd.nist.gov/vuln/detail/CVE-2023-24895
- https://github.com/dotnet/announcements/issues/261
- https://github.com/dotnet/wpf
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-24895
