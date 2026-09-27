# [M] Microsoft Security Advisory CVE-2026-62899 – .NET Security Feature Bypass Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r6mh-95jw-g7qg
CVE: CVE-2026-62899
CWE: CWE-444
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-11
Source: https://github.com/advisories/GHSA-r6mh-95jw-g7qg
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.osx-arm64` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=10.0.0 <10.0.11
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.NETCore.App.Runtime.osx-arm64` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=9.0.0 <9.0.19
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=8.0.0 <8.0.30
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=8.0.0 <8.0.30
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm` — affected >=8.0.0 <8.0.30
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=8.0.0 <8.0.30
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=8.0.0 <8.0.30
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=8.0.0 <8.0.30
- NuGet: `Microsoft.NETCore.App.Runtime.osx-arm64` — affected >=8.0.0 <8.0.30
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=8.0.0 <8.0.30

## Details
## Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in System.Net.HttpListener. This advisory also provides guidance on what developers can do to update their applications to remove this vulnerability.

Inconsistent interpretation of http requests ('http request/response smuggling') in .NET allows an unauthorized attacker to bypass a security feature over a network.

## Announcement

Announcement for this issue can be found at https://github.com/dotnet/announcements/issues/427

## CVSS Details

- **Version:** 3.1
- **Severity:** Medium
- **Score:** 5.9
- **Vector:** `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N/E:U/RL:O/RC:C`
- **Weakness:** CWE-444: Inconsistent Interpretation of HTTP Requests ('HTTP Request/Response Smuggling')

## Affected Platforms

- **Platforms:** Linux, macOS
- **Architectures:** All

## <a name="affected-packages"></a>Affected Packages
The vulnerability affects any Microsoft .NET project if it uses any of affected package versions listed below

### <a name=".NET 10"></a>.NET 10
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NETCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm) | >= 10.0.0, <= 10.0.10 | 10.0.11
[Microsoft.NETCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm64) | >= 10.0.0, <= 10.0.10 | 10.0.11
[Microsoft.NETCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm) | >= 10.0.0, <= 10.0.10 | 10.0.11
[Microsoft.NETCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm64) | >= 10.0.0, <= 10.0.10 | 10.0.11
[Microsoft.NETCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-x64) | >= 10.0.0, <= 10.0.10 | 10.0.11
[Microsoft.NETCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-x64) | >= 10.0.0, <= 10.0.10 | 10.0.11
[Microsoft.NETCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.osx-arm64) | >= 10.0.0, <= 10.0.10 | 10.0.11
[Microsoft.NETCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.osx-x64) | >= 10.0.0, <= 10.0.10 | 10.0.11

### <a name=".NET 9"></a>.NET 9
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NETCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm) | >= 9.0.0, <= 9.0.18 | 9.0.19
[Microsoft.NETCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm64) | >= 9.0.0, <= 9.0.18 | 9.0.19
[Microsoft.NETCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm) | >= 9.0.0, <= 9.0.18 | 9.0.19
[Microsoft.NETCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm64) | >= 9.0.0, <= 9.0.18 | 9.0.19
[Microsoft.NETCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-x64) | >= 9.0.0, <= 9.0.18 | 9.0.19
[Microsoft.NETCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-x64) | >= 9.0.0, <= 9.0.18 | 9.0.19
[Microsoft.NETCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.osx-arm64) | >= 9.0.0, <= 9.0.18 | 9.0.19
[Microsoft.NETCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.osx-x64) | >= 9.0.0, <= 9.0.18 | 9.0.19

### <a name=".NET 8"></a>.NET 8
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.NETCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm) | >= 8.0.0, <= 8.0.29 | 8.0.30
[Microsoft.NETCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-arm64) | >= 8.0.0, <= 8.0.29 | 8.0.30
[Microsoft.NETCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm) | >= 8.0.0, <= 8.0.29 | 8.0.30
[Microsoft.NETCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-arm64) | >= 8.0.0, <= 8.0.29 | 8.0.30
[Microsoft.NETCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-musl-x64) | >= 8.0.0, <= 8.0.29 | 8.0.30
[Microsoft.NETCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.linux-x64) | >= 8.0.0, <= 8.0.29 | 8.0.30
[Microsoft.NETCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.osx-arm64) | >= 8.0.0, <= 8.0.29 | 8.0.30
[Microsoft.NETCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.NETCore.App.Runtime.osx-x64) | >= 8.0.0, <= 8.0.29 | 8.0.30

## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If using a package listed in [affected packages](#affected-packages), users are exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

1. To fix the issue please install the latest version of .NET. If users have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt then to update Visual Studio, which will also update their .NET SDKs.
2. If a user application references the vulnerable package, update the package reference to the patched version. They can list the versions they have installed by running the `dotnet --info` command.

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

[CVE-2026-62899](https://www.cve.org/CVERecord?id=CVE-2026-62899)

### Acknowledgements

Miha Zupan with Microsoft

### Revisions

V1.0 (08/11/2026): Advisory published.

## References
- https://github.com/dotnet/runtime/security/advisories/GHSA-r6mh-95jw-g7qg
- https://nvd.nist.gov/vuln/detail/CVE-2026-62899
- https://github.com/dotnet/announcements/issues/427
- https://github.com/dotnet/runtime
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-62899
