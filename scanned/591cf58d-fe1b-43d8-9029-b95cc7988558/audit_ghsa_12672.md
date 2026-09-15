# [H] NuGet Client Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-6qmf-mmc7-6c2p
CVE: CVE-2023-29337
CWE: CWE-367
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-6qmf-mmc7-6c2p
Type: github-advisory

## Affected
- NuGet: `Microsoft.Build.NuGetSdkResolver` — affected 5.9.0-rc.7122
- NuGet: `NuGet.PackageManagement` — affected >=6.0.0 <6.0.5
- NuGet: `NuGet.PackageManagement` — affected >=6.2.0 <6.2.4
- NuGet: `NuGet.PackageManagement` — affected >=6.3.0 <6.3.3
- NuGet: `NuGet.PackageManagement` — affected >=6.4.0 <6.4.2
- NuGet: `NuGet.PackageManagement` — affected >=6.5.0 <6.5.1
- NuGet: `NuGet.PackageManagement` — affected >=6.6.0 <6.6.1
- NuGet: `Microsoft.Build.NuGetSdkResolver` — affected 5.10.0-rc.7240
- NuGet: `Microsoft.Build.NuGetSdkResolver` — affected 5.11.0-rc.10
- NuGet: `NuGet.Commands` — affected >=6.0.0 <6.0.5
- NuGet: `NuGet.Commands` — affected >=6.2.0 <6.2.4
- NuGet: `NuGet.Commands` — affected >=6.3.0 <6.3.3
- NuGet: `NuGet.Commands` — affected >=6.4.0 <6.4.2
- NuGet: `NuGet.Commands` — affected >=6.5.0 <6.5.1
- NuGet: `NuGet.Commands` — affected >=6.6.0 <6.6.1
- NuGet: `NuGet.CommandLine` — affected >=6.0.0 <6.0.5
- NuGet: `NuGet.CommandLine` — affected >=6.2.0 <6.2.4
- NuGet: `NuGet.CommandLine` — affected >=6.3.0 <6.3.3
- NuGet: `NuGet.CommandLine` — affected >=6.4.0 <6.4.2
- NuGet: `NuGet.CommandLine` — affected >=6.5.0 <6.5.1
- NuGet: `NuGet.CommandLine` — affected >=6.6.0 <6.6.1
- NuGet: `NuGet.Common` — affected >=6.0.0 <6.0.5
- NuGet: `NuGet.Common` — affected >=6.2.0 <6.2.4
- NuGet: `NuGet.Common` — affected >=6.3.0 <6.3.3
- NuGet: `NuGet.Common` — affected >=6.4.0 <6.4.2
- NuGet: `NuGet.Common` — affected >=6.5.0 <6.5.1
- NuGet: `NuGet.Common` — affected >=6.6.0 <6.6.1
- NuGet: `NuGet.Protocol` — affected >=6.0.0 <6.0.5
- NuGet: `NuGet.Protocol` — affected >=6.2.0 <6.2.4
- NuGet: `NuGet.Protocol` — affected >=6.3.0 <6.3.3
- NuGet: `NuGet.Protocol` — affected >=6.4.0 <6.4.2
- NuGet: `NuGet.Protocol` — affected >=6.5.0 <6.5.1
- NuGet: `NuGet.Protocol` — affected >=6.6.0 <6.6.1
- NuGet: `NuGet.PackageManagement` — affected >=4.6.0 <5.11.5
- NuGet: `NuGet.Commands` — affected >=4.6.0 <5.11.5
- NuGet: `NuGet.CommandLine` — affected >=4.6.0 <5.11.5
- NuGet: `NuGet.Common` — affected >=4.6.0 <5.11.5
- NuGet: `NuGet.Protocol` — affected >=4.7.0 <5.11.5

## Details
### Description
Microsoft is releasing this security advisory to provide information about a vulnerability in .NET and NuGet on Linux. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A vulnerability exists in .NET 6.0, .NET 7.0 and NuGet(nuget.exe, NuGet.Protocol, NuGet.Common, NuGet.CommandLine, NuGet.Commands, Microsoft.Build.NuGetSdkResolver, NuGet.PackageManagement) where a potential race condition that can lead to a symlink attack on Linux. Non-Linux platforms are not affected.

### Affected software
This issue only affects Linux systems.

#### NuGet & NuGet Packages

- Any NuGet.exe, NuGet.Protocol, NuGet.Common, NuGet.CommandLine, NuGet.Commands, Microsoft.Build.NuGetSdkResolver, NuGet.PackageManagement 6.6.0 version or earlier.
- Any NuGet.exe, NuGet.Protocol, NuGet.Common, NuGet.CommandLine, NuGet.Commands, Microsoft.Build.NuGetSdkResolver, NuGet.PackageManagement 6.5.0 version or earlier.
- Any NuGet.exe, NuGet.Protocol, NuGet.Common, NuGet.CommandLine, NuGet.Commands, Microsoft.Build.NuGetSdkResolver, NuGet.PackageManagement 6.4.1 version or earlier.
- Any NuGet.exe, NuGet.Protocol, NuGet.Common, NuGet.CommandLine, NuGet.Commands, Microsoft.Build.NuGetSdkResolver, NuGet.PackageManagement 6.3.2 version or earlier.
- Any NuGet.exe, NuGet.Protocol, NuGet.Common, NuGet.CommandLine, NuGet.Commands, Microsoft.Build.NuGetSdkResolver, NuGet.PackageManagement 6.2.3 version or earlier.
- Any NuGet.exe, NuGet.Protocol, NuGet.Common, NuGet.CommandLine, NuGet.Commands, Microsoft.Build.NuGetSdkResolver, NuGet.PackageManagement 6.0.4 version or earlier.
- Any NuGet.exe, NuGet.Protocol, NuGet.Common, NuGet.CommandLine, NuGet.Commands, Microsoft.Build.NuGetSdkResolver, NuGet.PackageManagement 5.11.4

#### .NET SDK(s)

- Any .NET SDK 7.0.106 or earlier, or 7.0.303 or earlier
- Any .NET SDK 6.0.117 or earlier, or 6.0.312 or earlier, or 6.0.409 or earlier.


### Patches
To fix the issue, please install the latest version of .NET 6.0 or .NET 7.0 and NuGet (NuGet.exe, NuGet.Protocol, NuGet.Common, NuGet.CommandLine, NuGet.Commands, NuGet.PackageManagement  versions). If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET SDKs.

- If you're using NuGet.exe 6.6.0 or lower, you should download and install 6.6.1 from https://dist.nuget.org/win-x86-commandline/v6.6.1/nuget.exe.
- If you're using NuGet.exe 6.5.0 or lower, you should download and install 6.5.1 from https://dist.nuget.org/win-x86-commandline/v6.5.1/nuget.exe.
- If you're using NuGet.exe 6.4.1 or lower, you should download and install 6.4.2 from https://dist.nuget.org/win-x86-commandline/v6.4.2/nuget.exe.
- If you're using NuGet.exe 6.3.2 or lower, you should download and install 6.3.3 from https://dist.nuget.org/win-x86-commandline/v6.3.3/nuget.exe.
- If you're using NuGet.exe 6.2.3 or lower, you should download and install 6.2.4 from https://dist.nuget.org/win-x86-commandline/v6.2.4/nuget.exe.
- If you're using NuGet.exe 6.0.4 or lower, you should download and install 6.0.5 from https://dist.nuget.org/win-x86-commandline/v6.0.5/nuget.exe.
- If you're using NuGet.exe 5.11.4 or lower, you should download and install 5.11.5 from https://dist.nuget.org/win-x86-commandline/v5.11.5/nuget.exe.
- If you're using .NET 7.0, you should download and install Runtime 7.0.7 or SDK 7.0.107 or SDK 7.0.304 from https://dotnet.microsoft.com/download/dotnet-core/7.0.

- If you're using .NET 7.0, you should download and install Runtime 7.0.7 or SDK 7.0.107 or SDK 7.0.304 from https://dotnet.microsoft.com/download/dotnet-core/7.0.
- If you're using .NET 6.0, you should download and install Runtime 6.0.18 or SDK 6.0.118 or SDK 6.0.312 from https://dotnet.microsoft.com/download/dotnet-core/6.0.


### Other details
Announcement for this issue can be found at https://github.com/NuGet/Announcements/issues/69

MSRC details for this can be found at https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-29337

## References
- https://github.com/NuGet/NuGet.Client/security/advisories/GHSA-6qmf-mmc7-6c2p
- https://nvd.nist.gov/vuln/detail/CVE-2023-29337
- https://github.com/NuGet/NuGet.Client/commit/7fe6b814c901490292f02d8ea12749505fbb959a
- https://github.com/NuGet/NuGet.Client
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-29337
