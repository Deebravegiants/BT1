# [H] Microsoft Security Advisory CVE-2025-55247 | .NET Denial of Service Vulnerability

## Summary
Severity: High
Advisory: GHSA-w3q9-fxm7-j8fq
CVE: CVE-2025-55247
CWE: CWE-59
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-w3q9-fxm7-j8fq
Type: github-advisory

## Affected
- NuGet: `Microsoft.Build.Tasks.Core` — affected >=17.15.0-preview-25277-114 <18.0.0-preview-25476-107
- NuGet: `Microsoft.Build.Tasks.Core` — affected >=17.14.0 <17.14.28
- NuGet: `Microsoft.Build.Tasks.Core` — affected >=17.12.0 <17.12.50
- NuGet: `Microsoft.Build.Tasks.Core` — affected >=17.11.0 <17.11.48
- NuGet: `Microsoft.Build.Tasks.Core` — affected >=17.10.0 <17.10.46
- NuGet: `Microsoft.Build.Tasks.Core` — affected >=17.8.0 <17.8.43
- NuGet: `Microsoft.Build` — affected >=17.15.0-preview-25277-114 <18.0.0-preview-25476-107
- NuGet: `Microsoft.Build` — affected >=17.14.0 <17.14.28
- NuGet: `Microsoft.Build` — affected >=17.12.0 <17.12.50
- NuGet: `Microsoft.Build` — affected >=17.11.0 <17.11.48
- NuGet: `Microsoft.Build` — affected >=17.10.0 <17.10.46
- NuGet: `Microsoft.Build` — affected >=17.8.0 <17.8.43
- NuGet: `Microsoft.Build.Utilities.Core` — affected >=17.15.0-preview-25277-114 <18.0.0-preview-25476-107
- NuGet: `Microsoft.Build.Utilities.Core` — affected >=17.14.0 <17.14.28
- NuGet: `Microsoft.Build.Utilities.Core` — affected >=17.12.0 <17.12.50
- NuGet: `Microsoft.Build.Utilities.Core` — affected >=17.11.0 <17.11.48
- NuGet: `Microsoft.Build.Utilities.Core` — affected >=17.10.0 <17.10.46
- NuGet: `Microsoft.Build.Utilities.Core` — affected >=17.8.0 <17.8.43

## Details
# Microsoft Security Advisory CVE-2025-55247 | .NET Denial of Service Vulnerability

## <a name="executive-summary"></a>Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 8.0.xxx, .NET 9.0.xxx and .NET 10.0.xxx. This advisory also provides guidance on what developers can do to update their environments to remove this vulnerability.

A vulnerability exists in .NET where predictable paths for MSBuild's temporary directories on Linux let another user create the directories ahead of MSBuild, leading to DoS of builds. This only affects .NET on Linux operating systems.

## Announcement

Announcement for this issue can be found at  https://github.com/dotnet/announcements/issues/370

### <a name="mitigation-factors"></a>Mitigation factors

Projects which do not utilize the [DownloadFile](https://learn.microsoft.com/visualstudio/msbuild/downloadfile-task)  build task are not susceptible to this vulnerability.

## <a name="affected-software"></a>Affected software

* Any installation of .NET 10.0.100-rc.1.25451.107 SDK or earlier.
* Any installation of .NET 9.0.110 SDK, .NET 9.0.305 SDK or earlier.
* Any installation of .NET 8.0.120 SDK, .NET 8.0.317 SDK, .NET 8.0.414 SDK or earlier.

## <a name="affected-packages"></a>Affected Packages

The vulnerability affects any Microsoft .NET Core project if it uses any of affected packages versions listed below

Package name |Affected version | Patched version
------------ |---------------- | -------------------------
[Microsoft.Build.Tasks.Core](https://www.nuget.org/packages/Microsoft.Build.Tasks.Core) | 17.15.0-preview-25277-114 <br />>=17.14.0, <= 17.14.8 <br />>= 17.12.0, <= 17.12.36 <br/> >= 17.11.0, <= 17.11.31<br />  >= 17.10.0, <= 17.10.29 <br />  >= 17.8.0, <= 17.8.29 <br /> | 18.0.0-preview-25476-107 <br />17.14.28 <br />17.12.50 <br/>17.11.48 <br />17.10.46 <br />17.8.43 <br />


Package name|Affected version | Patched version
------------ |---------------|----------------
[Microsoft.Build](https://www.nuget.org/packages/Microsoft.Build) | 17.15.0-preview-25277-114 <br />>=17.14.0, <= 17.14.8 <br />>= 17.12.0, <= 17.12.36 <br/> >= 17.11.0, <= 17.11.31<br />  >= 17.10.0, <= 17.10.29 <br />  >= 17.8.0, <= 17.8.29 <br /> | 18.0.0-preview-25476-107 <br />17.14.28 <br />17.12.50 <br/>17.11.48 <br />17.10.46 <br />17.8.43 <br />

Package name  |Affected version | Patched version
------------ |---------------|----------------
[Microsoft.Build.Utilities.core](https://www.nuget.org/packages/Microsoft.Build.Utilities.Core/17.15.0-preview-25277-114)| 17.15.0-preview-25277-114 <br />>=17.14.0, <= 17.14.8 <br />>= 17.12.0, <= 17.12.36 <br/> >= 17.11.0, <= 17.11.31<br />  >= 17.10.0, <= 17.10.29 <br />  >= 17.8.0, <= 17.8.29 <br /> | 18.0.0-preview-25476-107 <br />17.14.28 <br />17.12.50 <br/>17.11.48 <br />17.10.46 <br />17.8.43 <br />

## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If you have a .NET SDK with a version listed, or an affected package listed in [affected software](#affected-packages) or [affected packages](#affected-software), you're exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

1. To fix the issue please install the latest version of .NET 10.0 SDK, .NET 9.0 SDK or .NET 8.0 SDK. If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET  SDKs.
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

* If you're using .NET 10.0, you should download and install the appropriate SDK: `.NET 10.0.100-rc.2.25502.107` for Visual Studio 2026 v18 Preview 3. Download from https://dotnet.microsoft.com/download/dotnet-core/10.0.

* If you're using .NET 9.0, you should download and install the appropriate SDK: `.NET 9.0.306` for Visual Studio 2022 v17.14 or `.NET 9.0.111` for v17.12. Download from https://dotnet.microsoft.com/download/dotnet-core/9.0.

* If you're using .NET 8.0, you should download and install the appropriate SDK: `.NET 8.0.415` for Visual Studio 2022 v17.11, `.NET 8.0.318` for v17.10, or `.NET 8.0.121` for v17.8. Download from https://dotnet.microsoft.com/download/dotnet-core/8.0.

Once you have installed the updated SDK, restart your apps for the update to take effect.

## Other Information

### Reporting Security Issues

If you have found a potential security issue in .NET 8.0, .NET 9.0 or .NET 10.0, please email details to secure@microsoft.com. Reports may qualify for the Microsoft .NET Core & .NET 5 Bounty. Details of the Microsoft .NET Bounty Program including terms and conditions are at <https://aka.ms/corebounty>.

### Support

You can ask questions about this issue on GitHub in the .NET GitHub organization. The main repos are located at https://github.com/dotnet/runtime. The Announcements repo (https://github.com/dotnet/Announcements) will contain this bulletin as an issue and will include a link to a discussion issue. You can ask questions in the linked discussion issue.

### Disclaimer

The information provided in this advisory is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

### External Links

[CVE-2025-55247]( https://www.cve.org/CVERecord?id=CVE-2025-55247)

### Revisions

V1.0 (October 14, 2025): Advisory published.

## References
- https://github.com/dotnet/msbuild/security/advisories/GHSA-w3q9-fxm7-j8fq
- https://nvd.nist.gov/vuln/detail/CVE-2025-55247
- https://github.com/dotnet/msbuild
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-55247
