# [M] Potential leak of NuGet.org API key

## Summary
Severity: Medium
Advisory: GHSA-3885-8gqc-3wpf
CVE: CVE-2022-30184
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-14
Source: https://github.com/advisories/GHSA-3885-8gqc-3wpf
Type: github-advisory

## Affected
- NuGet: `NuGet.Commands` — affected >=3.5.0 <4.9.5
- NuGet: `NuGet.CommandLine` — affected >=3.5.0 <4.9.5
- NuGet: `NuGet.CommandLine.XPlat` — affected >=3.5.0 <4.9.5
- NuGet: `NuGet.Commands` — affected >=5.0.0 <5.2.1
- NuGet: `NuGet.Commands` — affected >=5.3.0 <5.7.2
- NuGet: `NuGet.Commands` — affected >=5.8.0 <5.9.2
- NuGet: `NuGet.Commands` — affected >=5.10.0 <5.11.2
- NuGet: `NuGet.Commands` — affected >=6.0.0 <6.0.2
- NuGet: `NuGet.Commands` — affected >=6.1.0 <6.2.1
- NuGet: `NuGet.CommandLine` — affected >=5.0.0 <5.2.1
- NuGet: `NuGet.CommandLine` — affected >=5.3.0 <5.7.2
- NuGet: `NuGet.CommandLine` — affected >=5.8.0 <5.9.2
- NuGet: `NuGet.CommandLine` — affected >=5.10.0 <5.11.2
- NuGet: `NuGet.CommandLine` — affected >=6.0.0 <6.0.2
- NuGet: `NuGet.CommandLine` — affected >=6.1.0 <6.2.1
- NuGet: `NuGet.CommandLine.XPlat` — affected >=5.0.0 <5.2.1
- NuGet: `NuGet.CommandLine.XPlat` — affected >=5.3.0 <5.7.2
- NuGet: `NuGet.CommandLine.XPlat` — affected >=5.8.0 <5.9.2
- NuGet: `NuGet.CommandLine.XPlat` — affected >=5.10.0 <5.11.2
- NuGet: `NuGet.CommandLine.XPlat` — affected >=6.0.0 <6.0.2
- NuGet: `NuGet.CommandLine.XPlat` — affected >=6.1.0 <6.2.1

## Details
### Description 

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 6.0 and .NET Core 3.1, NuGet (NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.CommandLine.XPlat version range from 3.5.0 to 6.2.0). This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A vulnerability exists in .NET 6.0, .NET Core 3.1, and NuGet (NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.CommandLine.XPlat version range from 3.5.0 to 6.2.0) where a nuget.org api key could leak due to an incorrect comparison with a server url.

### Affected software 

#### NuGet & NuGet Packages

- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.CommandLine.XPlat 6.2.0 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.CommandLine.XPlat 6.0.1 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.CommandLine.XPlat 5.11.1 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.CommandLine.XPlat 5.9.1 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.CommandLine.XPlat 5.7.1 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.CommandLine.XPlat 4.9.4 version or earlier.

#### .NET SDK(s)

- Any .NET 6.0 application running on .NET 6.0.5 or earlier.
- Any .NET 3.1 application running on .NET Core 3.1.25 or earlier.

### Patches 

- If you're using NuGet.exe 6.2.0 or lower, you should download and install 6.2.1 from https://dist.nuget.org/win-x86-commandline/v6.2.1/nuget.exe. 

- If you're using NuGet.exe 6.0.1 or lower, you should download and install 6.0.2 from https://dist.nuget.org/win-x86-commandline/v6.0.2/nuget.exe. 

- If you're using NuGet.exe 5.11.1 or lower, you should download and install 5.11.2 from https://dist.nuget.org/win-x86-commandline/v5.11.2/nuget.exe. 

- If you're using NuGet.exe 5.9.1 or lower, you should download and install 5.9.2 from https://dist.nuget.org/win-x86-commandline/v5.9.2/nuget.exe. 

- If you're using NuGet.exe 5.7.1 or lower, you should download and install 5.7.2 from https://dist.nuget.org/win-x86-commandline/v4.7.2/nuget.exe. 

- If you're using NuGet.exe 4.9.4 or lower, you should download and install 4.9.5 from https://dist.nuget.org/win-x86-commandline/v4.9.5/nuget.exe. 

- If you're using .NET Core 6.0, you should download and install Runtime 6.0.6 or SDK 6.0.106 (for Visual Studio 2022 v17.0) or SDK 6.0.301 (for Visual Studio 2022 v17.2)  from https://dotnet.microsoft.com/download/dotnet-core/6.0. 

- If you're using .NET Core 3.1, you should download and install Runtime 3.1.26 or SDK 3.1.420 (for Visual Studio 2019 v16.9 or Visual Studio 2011 16.11 or Visual Studio 2022 17.0 or Visual Studio 2022 17.1 ) from https://dotnet.microsoft.com/download/dotnet-core/3.1 

.NET 6.0 and .NET Core 3.1 updates are also available from Microsoft Update. To access this either type "Check for updates" in your Windows search, or open Settings, choose Update & Security and then click Check for Updates. 

### Other Details 

Announcement for this issue can be found at https://github.com/NuGet/Announcements/issues/62
 
MSRC details for this can be found at https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2022-30184

## References
- https://github.com/NuGet/NuGet.Client/security/advisories/GHSA-3885-8gqc-3wpf
- https://nvd.nist.gov/vuln/detail/CVE-2022-30184
- https://github.com/NuGet/Home/issues/11883#issuecomment-1156194755
- https://github.com/NuGet/NuGet.Client/commit/ec6e62a645ec6b53a8784bf4571cac7786fd700b#diff-9e678e6dcc29381eb7c564f0e75ffc3ffc35458eca412c35b6404340b698d074R58-R65
- https://github.com/NuGet/NuGet.Client
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DMP34G53EA2DBTBLFOAQCDZRRENE2EA2
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XWNH4AC3LFVX35MDRX5OBZDGD2AMH66K
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DMP34G53EA2DBTBLFOAQCDZRRENE2EA2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWNH4AC3LFVX35MDRX5OBZDGD2AMH66K
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-30184
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2022-30184
