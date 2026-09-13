# [M] Microsoft Security Advisory CVE-2026-45491 – .NET Tampering Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7q4v-2mr6-5gpx
CVE: CVE-2026-45491
CWE: CWE-59
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-7q4v-2mr6-5gpx
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=8.0.0 <8.0.28
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=9.0.0 <9.0.17
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=10.0.0 <10.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=8.0.0 <8.0.28
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=9.0.0 <9.0.17
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=10.0.0 <10.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.osx-arm64` — affected >=8.0.0 <8.0.28
- NuGet: `Microsoft.NETCore.App.Runtime.osx-arm64` — affected >=9.0.0 <9.0.17
- NuGet: `Microsoft.NETCore.App.Runtime.osx-arm64` — affected >=10.0.0 <10.0.9

## Details
## Executive Summary

Microsoft is releasing this security advisory to provide information about a vulnerability in System.Formats.Tar. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A tampering vulnerability exists in the `TarFile.ExtractToDirectory` method where a symlink path traversal enables an attacker to perform arbitrary file writes outside the intended extraction directory.

## Announcement

Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/404

## Affected Platforms

- **Platforms:** All
- **Architectures:** All

## Affected Packages
The vulnerability affects any Microsoft .NET project if it uses any of affected package versions listed below

### .NET 10
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NETCore.App.Runtime](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime) | >= 10.0.0, <= 10.0.8 | 10.0.9

### .NET 9
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NETCore.App.Runtime](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime) | >= 9.0.0, <= 9.0.16 | 9.0.17

### .NET 8
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NETCore.App.Runtime](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime) | >= 8.0.0, <= 8.0.27 | 8.0.28

## Advisory FAQ

### How do I know if I am affected?

If using a package listed in affected packages, you're exposed to the vulnerability.

### How do I fix the issue?

1. To fix the issue please install the latest version of .NET 8.0, .NET 9.0, or .NET 10.0, as appropriate. If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET SDKs.
2. If your application references the vulnerable package, update the package reference to the patched version.

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

### Acknowledgements
Anonymous, Ashmit Sharma, Ky0toFu ,phrolo7a

### Revisions

V1.0 (June 9, 2026): Advisory published.

## References
- https://github.com/dotnet/runtime/security/advisories/GHSA-7q4v-2mr6-5gpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45491
- https://github.com/dotnet/announcements/issues/404
- https://github.com/dotnet/runtime
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-45491
