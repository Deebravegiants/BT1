# [H] Microsoft Security Advisory CVE-2026-62897 – .NET Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-fx4q-gjrx-2jw6
CVE: CVE-2026-62897
CWE: CWE-190
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-11
Source: https://github.com/advisories/GHSA-fx4q-gjrx-2jw6
Type: github-advisory

## Affected
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-arm64` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x64` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x86` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-arm64` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x64` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x86` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-arm64` — affected >=8.0.0 <8.0.30
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x64` — affected >=8.0.0 <8.0.30
- NuGet: `Microsoft.WindowsDesktop.App.Runtime.win-x86` — affected >=8.0.0 <8.0.30

## Details
## Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in Windows Presentation Foundation. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

An integer overflow or wraparound in .NET allows an unauthorized attacker to execute code locally.

## Announcement

Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/434

## CVSS Details

- **Version:** 3.1
- **Severity:** High
- **Score:** 7.0
- **Vector:** `CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H/E:U/RL:O/RC:C`
- **Weakness:** CWE-190: Integer Overflow or Wraparound

## Affected Platforms

- **Platforms:** Windows
- **Architectures:** All

## <a name="affected-packages"></a>Affected Packages
The vulnerability affects any Microsoft .NET project if it uses any of affected package versions listed below

### <a name=".NET 10"></a>.NET 10
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.WindowsDesktop.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-arm64) | >= 10.0.0, <= 10.0.10 | 10.0.11
[Microsoft.WindowsDesktop.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x64) | >= 10.0.0, <= 10.0.10 | 10.0.11
[Microsoft.WindowsDesktop.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x86) | >= 10.0.0, <= 10.0.10 | 10.0.11

### <a name=".NET 9"></a>.NET 9
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.WindowsDesktop.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-arm64) | >= 9.0.0, <= 9.0.18 | 9.0.19
[Microsoft.WindowsDesktop.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x64) | >= 9.0.0, <= 9.0.18 | 9.0.19
[Microsoft.WindowsDesktop.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x86) | >= 9.0.0, <= 9.0.18 | 9.0.19

### <a name=".NET 8"></a>.NET 8
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.WindowsDesktop.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-arm64) | >= 8.0.0, <= 8.0.29 | 8.0.30
[Microsoft.WindowsDesktop.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x64) | >= 8.0.0, <= 8.0.29 | 8.0.30
[Microsoft.WindowsDesktop.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.WindowsDesktop.App.Runtime.win-x86) | >= 8.0.0, <= 8.0.29 | 8.0.30

## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If using a package listed in [affected packages](#affected-packages), an application is exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

1. To fix the issue please install the latest version of .NET. If users have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt them to update Visual Studio, which will also update their .NET SDKs.
2. If a user's application references the vulnerable package, update the package reference to the patched version. Users can list the versions they have installed by running the `dotnet --info` command.

Once users have installed the updated runtime or SDK, they should restart their apps for the update to take effect.

Additionally, if they've deployed [self-contained applications](https://docs.microsoft.com/dotnet/core/deploying/#self-contained-deployments-scd) targeting any of the impacted versions, these applications are also vulnerable and must be recompiled and redeployed.

## Other Information

### Reporting Security Issues

If users have found a potential security issue in a supported version of .NET, please report it to the Microsoft Security Response Center (MSRC) via the [MSRC Researcher Portal](https://msrc.microsoft.com/report/vulnerability/new). Further information can be found in the MSRC [Report an Issue FAQ](https://www.microsoft.com/msrc/faqs-report-an-issue).

Security reports made through MSRC may qualify for the Microsoft .NET Bounty. Details of the Microsoft .NET Bounty Program including terms and conditions are at https://aka.ms/corebounty.

### Support

Users can ask questions about this issue on GitHub in the .NET GitHub organization. The main repos are located at https://github.com/dotnet/runtime. The Announcements repo (https://github.com/dotnet/Announcements) will contain this bulletin as an issue and will include a link to a discussion issue. Users can ask questions in the linked discussion issue.

### Disclaimer

The information provided in this advisory is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.

### External Links

[CVE-2026-62897](https://www.cve.org/CVERecord?id=CVE-2026-62897)

### Acknowledgements

41ae55e9310ff27fa6f26af4727e5590

### Revisions

V1.0 (08/11/2026): Advisory published.

## References
- https://github.com/dotnet/wpf/security/advisories/GHSA-fx4q-gjrx-2jw6
- https://nvd.nist.gov/vuln/detail/CVE-2026-62897
- https://github.com/dotnet/announcements/issues/434
- https://github.com/dotnet/wpf
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-62897
