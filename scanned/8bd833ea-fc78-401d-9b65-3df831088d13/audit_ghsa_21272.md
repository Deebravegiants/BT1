# [H] NuGet Elevation of Privilege Vulnerability

## Summary
Severity: High
Advisory: GHSA-g3q9-xf95-8hp5
CVE: CVE-2022-41032
CWE: CWE-269
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-11
Source: https://github.com/advisories/GHSA-g3q9-xf95-8hp5
Type: github-advisory

## Affected
- NuGet: `NuGet.Commands` — affected >=4.6.0 <4.9.6
- NuGet: `NuGet.Commands` — affected >=5.0.0 <5.7.3
- NuGet: `NuGet.Commands` — affected >=5.8.0 <5.9.3
- NuGet: `NuGet.Commands` — affected >=5.10.0 <5.11.3
- NuGet: `NuGet.Commands` — affected >=6.0.0 <6.0.3
- NuGet: `NuGet.Commands` — affected >=6.1.0 <6.2.2
- NuGet: `NuGet.Commands` — affected >=6.3.0 <6.3.1
- NuGet: `NuGet.CommandLine` — affected >=4.6.0 <4.9.6
- NuGet: `NuGet.CommandLine` — affected >=5.0.0 <5.7.3
- NuGet: `NuGet.CommandLine` — affected >=5.8.0 <5.9.3
- NuGet: `NuGet.CommandLine` — affected >=5.10.0 <5.11.3
- NuGet: `NuGet.CommandLine` — affected >=6.0.0 <6.0.3
- NuGet: `NuGet.CommandLine` — affected >=6.1.0 <6.2.2
- NuGet: `NuGet.CommandLine` — affected >=6.3.0 <6.3.1
- NuGet: `NuGet.Protocol` — affected >=4.6.0 <4.9.6
- NuGet: `NuGet.Protocol` — affected >=5.0.0 <5.7.3
- NuGet: `NuGet.Protocol` — affected >=5.8.0 <5.9.3
- NuGet: `NuGet.Protocol` — affected >=5.10.0 <5.11.3
- NuGet: `NuGet.Protocol` — affected >=6.0.0 <6.0.3
- NuGet: `NuGet.Protocol` — affected >=6.1.0 <6.2.2
- NuGet: `NuGet.Protocol` — affected >=6.3.0 <6.3.1

## Details
## Description

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET 7.0.0-rc, .NET 6.0, .NET Core 3.1, and NuGet (NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol). This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A vulnerability exists in .NET 7.0.0-rc.1, .NET 6.0, .NET Core 3.1, and NuGet clients (NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol) where a malicious actor could cause a user to execute arbitrary code.

## Affected software

### NuGet & NuGet Packages

- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol 6.3.0 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol 6.2.1 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol 6.0.2 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol 5.11.2 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol 5.9.2 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol 5.7.2 version or earlier.
- Any NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol 4.9.5 version or earlier.

### .NET SDK(s)

- Any .NET 6.0 application running on .NET 6.0.9 or earlier.
- Any .NET 3.1 application running on .NET Core 3.1.29 or earlier.

## Patches

To fix the issue, please install the latest version of .NET 6.0 or .NET Core 3.1 and NuGet (NuGet.exe, NuGet.Commands, NuGet.CommandLine, NuGet.Protocol versions). If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET SDKs.

- If you're using NuGet.exe 6.3.0 or lower, you should download and install 6.3.1 from https://dist.nuget.org/win-x86-commandline/v6.3.1/nuget.exe .

- If you're using NuGet.exe 6.2.1 or lower, you should download and install 6.2.2 from https://dist.nuget.org/win-x86-commandline/v6.2.2/nuget.exe .

- If you're using NuGet.exe 6.0.2 or lower, you should download and install 6.0.3 from https://dist.nuget.org/win-x86-commandline/v6.0.3/nuget.exe .

- If you're using NuGet.exe 5.11.2 or lower, you should download and install 5.11.3 from https://dist.nuget.org/win-x86-commandline/v5.11.3/nuget.exe .

- If you're using NuGet.exe 5.9.2 or lower, you should download and install 5.9.3 from https://dist.nuget.org/win-x86-commandline/v5.9.3/nuget.exe .

- If you're using NuGet.exe 5.7.2 or lower, you should download and install 5.7.3 from https://dist.nuget.org/win-x86-commandline/v5.7.3/nuget.exe .

- If you're using NuGet.exe 4.9.5 or lower, you should download and install 4.9.6 from https://dist.nuget.org/win-x86-commandline/v4.9.6/nuget.exe .

- If you're using .NET Core 6.0, you should download and install Runtime 6.0.10 or SDK 6.0.110 (for Visual Studio 2022 v17.0) or SDK 6.0.402 (for Visual Studio 2022 v17.3) from https://dotnet.microsoft.com/download/dotnet-core/6.0.

- If you're using .NET Core 3.1, you should download and install Runtime 3.1.30 or SDK 3.1.424 (for Visual Studio 2019 v16.9 or Visual Studio 2019 v16.11 or Visual Studio 2022 v17.0 or Visual Studio 2022 v17.1) from https://dotnet.microsoft.com/download/dotnet-core/3.1.

.NET 6.0 and .NET Core 3.1 updates are also available from Microsoft Update. To access this either type "Check for updates" in your Windows search, or open Settings, choose Update & Security and then click Check for Updates.

## Other details

Announcement for this issue can be found at https://github.com/NuGet/Announcements/issues/65

MSRC details for this can be found at https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2022-41032

## References
- https://github.com/NuGet/NuGet.Client/security/advisories/GHSA-g3q9-xf95-8hp5
- https://nvd.nist.gov/vuln/detail/CVE-2022-41032
- https://github.com/NuGet/Announcements/issues/65
- https://github.com/NuGet/NuGet.Client/commit/6392863cf83f4870e18f1d02f2463cca633e59ed
- https://github.com/NuGet/NuGet.Client
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FOG35Z5RL5W5RGLLYLN46CI4D2UPDSWM
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HDPT2MJC3HD7HYZGASOOX6MTDR4ASBL5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X7BMHO5ITRBZREVTEKHQRGSFRPDMALV3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FOG35Z5RL5W5RGLLYLN46CI4D2UPDSWM
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HDPT2MJC3HD7HYZGASOOX6MTDR4ASBL5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X7BMHO5ITRBZREVTEKHQRGSFRPDMALV3
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-41032
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2022-41032
- https://www.edwardthomson.com/blog/my-first-cve.html
