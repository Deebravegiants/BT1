# [C] NuGet Client Security Feature Bypass Vulnerability 

## Summary
Severity: Critical
Advisory: GHSA-68w7-72jg-6qpp
CVE: CVE-2024-0057
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-68w7-72jg-6qpp
Type: github-advisory

## Affected
- NuGet: `NuGet.CommandLine` — affected >=4.6.0 <5.11.6
- NuGet: `NuGet.Packaging` — affected >=4.6.0 <5.11.6
- NuGet: `NuGet.CommandLine` — affected >=6.0.0 <6.0.6
- NuGet: `NuGet.Packaging` — affected >=6.0.0 <6.0.6
- NuGet: `NuGet.CommandLine` — affected >=6.3.0 <6.3.4
- NuGet: `NuGet.Packaging` — affected >=6.3.0 <6.3.4
- NuGet: `NuGet.CommandLine` — affected >=6.4.0 <6.4.3
- NuGet: `NuGet.Packaging` — affected >=6.4.0 <6.4.3
- NuGet: `NuGet.CommandLine` — affected >=6.6.0 <6.6.2
- NuGet: `NuGet.Packaging` — affected >=6.6.0 <6.6.2
- NuGet: `NuGet.CommandLine` — affected >=6.7.0 <6.7.1
- NuGet: `NuGet.Packaging` — affected >=6.7.0 <6.7.1
- NuGet: `NuGet.CommandLine` — affected >=6.8.0 <6.8.1
- NuGet: `NuGet.Packaging` — affected >=6.8.0 <6.8.1

## Details
### Description
Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 6.0, .NET 7.0 and .NET 8.0. This advisory also provides guidance on what developers can do to update their applications to address this vulnerability. 

A security feature bypass vulnerability exists when Microsoft .NET Framework-based applications use X.509 chain building APIs but do not completely validate the X.509 certificate due to a logic flaw. An attacker could present an arbitrary untrusted certificate with malformed signatures, triggering a bug in the framework. The framework will correctly report that X.509 chain building failed, but it will return an incorrect reason code for the failure. Applications which utilize this reason code to make their own chain building trust decisions may inadvertently treat this scenario as a successful chain build. This could allow an adversary to subvert the app's typical authentication logic. 

### Affected software
#### NuGet & NuGet Packages
- Any NuGet.exe, NuGet.CommandLine, NuGet.Packaging 6.8.0 version or earlier. 
- Any NuGet.exe, NuGet.CommandLine, NuGet.Packaging 6.7.0 version or earlier. 
- Any NuGet.exe, NuGet.CommandLine, NuGet.Packaging 6.6.1 version or earlier. 
- Any NuGet.exe, NuGet.CommandLine, NuGet.Packaging 6.4.2 version or earlier. 
- Any NuGet.exe, NuGet.CommandLine, NuGet.Packaging 6.3.3 version or earlier. 
- Any NuGet.exe, NuGet.CommandLine, NuGet.Packaging 6.0.5 version or earlier. 
- Any NuGet.exe, NuGet.CommandLine, NuGet.Packaging 5.11.5 version or earlier. 

#### .NET SDK(s)
- Any .NET SDK 6.0.126 or earlier, or 6.0.418 or earlier.
- Any .NET SDK 7.0.115 or earlier, or 7.0.312 or earlier, or 7.0.405 or earlier.
- Any .NET SDK 8.0.101 or earlier.
 
### Patches
To fix the issue, please install the latest version of .NET 6.0, .NET 7.0 or .NET 8.0 and NuGet (NuGet.exe, NuGet.CommandLine, NuGet. Packaging versions). If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET SDKs. 
- If you're using NuGet.exe 6.8.0 or lower, you should download and install 6.8.1 from https://dist.nuget.org/win-x86-commandline/v6.8.1/nuget.exe. 
- If you're using NuGet.exe 6.7.0 or lower, you should download and install 6.7.1 from https://dist.nuget.org/win-x86-commandline/v6.7.1/nuget.exe. 
- If you're using NuGet.exe 6.6.1 or lower, you should download and install 6.6.2 from https://dist.nuget.org/win-x86-commandline/v6.6.2/nuget.exe. 
- If you're using NuGet.exe 6.4.2 or lower, you should download and install 6.4.3 from https://dist.nuget.org/win-x86-commandline/v6.4.3/nuget.exe. 
- If you're using NuGet.exe 6.3.3 or lower, you should download and install 6.3.4 from https://dist.nuget.org/win-x86-commandline/v6.3.4/nuget.exe. 
- If you're using NuGet.exe 6.0.5 or lower, you should download and install 6.0.6 from https://dist.nuget.org/win-x86-commandline/v6.0.6/nuget.exe. 
- If you're using NuGet.exe 5.11.5 or lower, you should download and install 5.11.6 from https://dist.nuget.org/win-x86-commandline/v5.11.6/nuget.exe. 
- If you're using .NET 8.0, you should download and install .NET 8.0.102 SDK (for Visual Studio 2022 v17.8) from https://dotnet.microsoft.com/download/dotnet-core/8.0 . 
- If you're using .NET 7.0, you should download and install SDK 7.0.116 (for Visual Studio 2022 v17.4), or SDK 7.0.313 (for Visual Studio 2022 v17.6), or 7.0.406 (for Visual Studio 2022 v17.7) from https://dotnet.microsoft.com/download/dotnet-core/7.0 . 
- If you're using .NET 6.0, you should download and install SDK 6.0.127 or SDK 6.0.419 (for Visual Studio 2022 v17.3) from https://dotnet.microsoft.com/download/dotnet-core/6.0 . 

### Other details
Announcement for this issue can be found at https://github.com/NuGet/Announcements/issues/71 

MSRC details for this can be found at [CVE-2024-0057 - Security Update Guide - Microsoft - NET, .NET Framework, and Visual Studio Security Feature Bypass Vulnerability](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-0057)

## References
- https://github.com/NuGet/NuGet.Client/security/advisories/GHSA-68w7-72jg-6qpp
- https://nvd.nist.gov/vuln/detail/CVE-2024-0057
- https://github.com/NuGet/NuGet.Client/commit/3333f352ec47f0ebb489f20353dea7017f6cb00c
- https://github.com/NuGet/NuGet.Client/commit/5e1ba955cca14328d2cb5723f211d5fbc9bcacb3
- https://github.com/NuGet/NuGet.Client
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-0057
- https://security.netapp.com/advisory/ntap-20240208-0007
