# [H] Microsoft Security Advisory CVE-2024-38168 | .NET Denial of Service Vulnerability

## Summary
Severity: High
Advisory: GHSA-7qrv-8f9x-3h32
CVE: CVE-2024-38168
CWE: CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-13
Source: https://github.com/advisories/GHSA-7qrv-8f9x-3h32
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm` — affected >=8.0.0 <8.0.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm64` — affected >=8.0.0 <8.0.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x64` — affected >=8.0.0 <8.0.8
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x86` — affected >=8.0.0 <8.0.8

## Details
# Microsoft Security Advisory CVE-2024-38168 | .NET Denial of Service Vulnerability

## <a name="executive-summary"></a>Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 8.0. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A vulnerability exists in .NET when an attacker through unauthenticated requests may trigger a Denial of Service in ASP.NET HTTP.sys web server. This is a windows OS only vulnerability.

## Announcement

Announcement for this issue can be found at  https://github.com/dotnet/announcements/issues/320

## <a name="mitigation-factors"></a>Mitigation factors

Microsoft has not identified any mitigating factors for this vulnerability.

## <a name="affected-software"></a>Affected software

* Any .NET 8.0 application running on .NET 8.0.7 or earlier.

## <a name="affected-packages"></a>Affected Packages
The vulnerability affects any Microsoft .NET Core project if it uses any of affected packages versions listed below

### <a name=".NET 8"></a>.NET 8
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.AspNetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm)                   | >= 8.0.0, < 8.0.8 | 8.0.8
[Microsoft.AspNetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm64)               | >= 8.0.0, < 8.0.8 | 8.0.8
[Microsoft.AspNetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x64)                   | >= 8.0.0, < 8.0.8 | 8.0.8
[Microsoft.AspNetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x86)                   | >= 8.0.0, < 8.0.8 | 8.0.8


## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If you have a runtime or SDK with a version listed, or an affected package listed in [affected software](#affected-packages) or [affected packages](#affected-software), you're exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

* To fix the issue please install the latest version of .NET 8.0 or .NET 6.0. If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET  SDKs.
* If you have .NET 6.0 or greater installed, you can list the versions you have installed by running the `dotnet --info` command. You will see output like the following;

```
.NET Core SDK (reflecting any global.json):


 Version:   8.0.200
 Commit:    8473146e7d

Runtime Environment:

 OS Name:     Windows
 OS Version:  10.0.18363
 OS Platform: Windows
 RID:         win10-x64
 Base Path:   C:\Program Files\dotnet\sdk\6.0.300\

Host (useful for support):

  Version: 8.0.3
  Commit:  8473146e7d

.NET Core SDKs installed:

  8.0.200 [C:\Program Files\dotnet\sdk]

.NET Core runtimes installed:

  Microsoft.AspAspNetCore.App 8.0.3 [C:\Program Files\dotnet\shared\Microsoft.AspAspNetCore.App]
  Microsoft.AspNetCore.App 8.0.3 [C:\Program Files\dotnet\shared\Microsoft.AspNetCore.App]
  Microsoft.WindowsDesktop.App 8.0.3 [C:\Program Files\dotnet\shared\Microsoft.WindowsDesktop.App]


To install additional .NET Core runtimes or SDKs:
  https://aka.ms/dotnet-download
```

* If you're using .NET 8.0, you should download and install .NET 8.0.8  Runtime or .NET 8.0.108 SDK (for Visual Studio 2022 v17.8) from https://dotnet.microsoft.com/download/dotnet-core/8.0.

.NET 8.0 updates are also available from Microsoft Update. To access this either type "Check for updates" in your Windows search, or open Settings, choose Update & Security and then click Check for Updates.

Once you have installed the updated runtime or SDK, restart your apps for the update to take effect.

Additionally, if you've deployed [self-contained applications](https://docs.microsoft.com/dotnet/core/deploying/#self-contained-deployments-scd) targeting any of the impacted versions, these applications are also vulnerable and must be recompiled and redeployed.

## Other Information

### Reporting Security Issues

If you have found a potential security issue in .NET 8.0  or .NET 6.0, please email details to secure@microsoft.com. Reports may qualify for the Microsoft .NET Core & .NET 5 Bounty. Details of the Microsoft .NET Bounty Program including terms and conditions are at <https://aka.ms/corebounty>.

### Support

You can ask questions about this issue on GitHub in the .NET GitHub organization. The main repos are located at https://github.com/dotnet/runtime and https://github.com/dotnet/aspnet/. The Announcements repo (https://github.com/dotnet/Announcements) will contain this bulletin as an issue and will include a link to a discussion issue. You can ask questions in the linked discussion issue.

### Disclaimer

The information provided in this advisory is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

### External Links

[CVE-2024-38168]( https://www.cve.org/CVERecord?id=CVE-2024-38168)

### Revisions

V1.0 (August 13, 2024): Advisory published.

_Version 1.0_

_Last Updated 2024-08-13_

## References
- https://github.com/dotnet/aspnetcore/security/advisories/GHSA-7qrv-8f9x-3h32
- https://nvd.nist.gov/vuln/detail/CVE-2024-38168
- https://github.com/dotnet/aspnetcore
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-38168
