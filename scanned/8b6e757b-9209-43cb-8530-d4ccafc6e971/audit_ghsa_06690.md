# [M] Microsoft Security Advisory CVE-2026-50659 – .NET Spoofing Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-74jp-vm22-8q8x
CVE: CVE-2026-50659
CWE: CWE-116
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-74jp-vm22-8q8x
Type: github-advisory

## Affected
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm64` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm64` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-x64` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-x64` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.osx-arm64` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.osx-x64` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm64` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.win-x64` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.win-x86` — affected >=10.0.0 <10.0.10
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm64` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm64` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-x64` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.linux-x64` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.osx-arm64` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.osx-x64` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm64` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.win-x64` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.win-x86` — affected >=9.0.0 <9.0.18
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.linux-arm64` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-arm64` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.linux-musl-x64` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.linux-x64` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.osx-arm64` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.osx-x64` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.win-arm64` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.win-x64` — affected >=8.0.0 <8.0.29
- NuGet: `Microsoft.NetCore.App.Runtime.win-x86` — affected >=8.0.0 <8.0.29

## Details
## Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in .NET SMTP client (System.Net.Mail). This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

A spoofing vulnerability exists in the SMTP client implementation (System.Net.Mail) in .NET 8, .NET 9, and .NET 10, where an attacker can spoof messages during message routing.

## Announcement

Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/**TBD**

## CVSS Details

- **Version:** 3.1
- **Severity:** Medium
- **Score:** 6.5
- **Vector:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N`
- **Weakness:** CWE-116 (Improper Encoding or Escaping of Output)

## Affected Platforms

- **Platforms:** All
- **Architectures:** All

## <a name="affected-packages"></a>Affected Packages
The vulnerability affects any Microsoft .NET project if it uses any of affected package versions listed below

### <a name=".NET 10.0"></a>.NET 10.0
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm64)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm64)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-x64)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-x64)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-arm64)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-x64)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm64)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x64)               | >= 10.0.0, <= 10.0.9 | 10.0.10
[Microsoft.NetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x86)               | >= 10.0.0, <= 10.0.9 | 10.0.10

### <a name=".NET 9.0"></a>.NET 9.0
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm64)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm64)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-x64)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-x64)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-arm64)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-x64)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm64)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x64)               | >= 9.0.0, <= 9.0.17 | 9.0.18
[Microsoft.NetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x86)               | >= 9.0.0, <= 9.0.17 | 9.0.18

### <a name=".NET 8.0"></a>.NET 8.0
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-arm64)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-arm64)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-musl-x64)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.linux-x64)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-arm64)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.osx-x64)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-arm64)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x64)               | >= 8.0.0, <= 8.0.28 | 8.0.29
[Microsoft.NetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.NetCore.App.Runtime.win-x86)               | >= 8.0.0, <= 8.0.28 | 8.0.29

## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If using a package listed in [affected packages](#affected-packages), you're exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

1. To fix the issue please install the latest version of .NET. If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET SDKs.
2. If your application references the vulnerable nuget package, update the package reference to the patched version. You can list the versions you have installed by running the `dotnet --info` command.

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

### External Links

[CVE-2026-50659]( https://www.cve.org/CVERecord?id=CVE-2026-50659)

### Acknowledgements

hamayanhamayan

### Revisions

V1.0 (July 14, 2026): Advisory published.

## References
- https://github.com/dotnet/runtime/security/advisories/GHSA-74jp-vm22-8q8x
- https://nvd.nist.gov/vuln/detail/CVE-2026-50659
- https://github.com/dotnet/announcements/issues/423
- https://github.com/dotnet/runtime/issues/130716
- https://github.com/dotnet/runtime
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-50659
