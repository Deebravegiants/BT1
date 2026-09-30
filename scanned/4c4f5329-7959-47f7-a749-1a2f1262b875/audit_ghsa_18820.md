# [C] Microsoft Security Advisory CVE-2025-55315: .NET Security Feature Bypass Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5rrx-jjjq-q2r5
CVE: CVE-2025-55315
CWE: CWE-444
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-10-14
Source: https://github.com/advisories/GHSA-5rrx-jjjq-q2r5
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.Server.Kestrel.Core` — affected >=0 <2.3.6
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm64` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm64` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-x64` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-x64` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-arm64` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-x64` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm64` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x64` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x86` — affected >=10.0.0-rc.1.25451.107 <10.0.0-rc.2.25502.107
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-x64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-x64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-arm64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-x64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x64` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x86` — affected >=9.0.0 <9.0.10
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-arm64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-arm64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-musl-x64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.linux-x64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-arm64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.osx-x64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-arm64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x64` — affected >=8.0.0 <8.0.21
- NuGet: `Microsoft.AspNetCore.App.Runtime.win-x86` — affected >=8.0.0 <8.0.21

## Details
# Microsoft Security Advisory CVE-2025-55315: .NET Security Feature Bypass Vulnerability

## <a name="executive-summary"></a>Executive summary

Microsoft is releasing this security advisory to provide information about a vulnerability in ASP.NET Core 10.0 , ASP.NET Core 9.0 , ASP.NET Core 8.0, and ASP.NET Core 2.3. This advisory also provides guidance on what developers can do to update their applications to address this vulnerability.

Inconsistent interpretation of http requests ('http request/response smuggling') in ASP.NET Core allows an authorized attacker to bypass a security feature over a network.

## Discussion

Discussion for this issue can be found at https://github.com/dotnet/announcements/issues/371

### <a name="mitigation-factors"></a>Mitigation factors

Microsoft has not identified any mitigating factors for this vulnerability.

## <a name="affected-software"></a>Affected software

* Any ASP.NET Core 10.0 application running on ASP.NET Core 10.0.0-rc.1.25451.107 or earlier.
* Any ASP.NET Core 9.0 application running on ASP.NET Core 9.0.9 or earlier.
* Any ASP.NET Core application running on ASP.NET Core 8.0.20 or earlier.
* Any ASP.NET Core 2.x application consuming the package Microsoft.AspNetCore.Server.Kestrel.Core version 2.3.0 or earlier.

## <a name="affected-packages"></a>Affected Packages
The vulnerability affects any Microsoft .NET Core project if it uses any of affected packages versions listed below

Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.AspNetCore.Server.Kestrel.Core](https://www.nuget.org/packages/Microsoft.AspNetCore.Server.Kestrel.Core) | <= 2.3.0  | 2.3.6

### <a name="ASP.NET Core 10"></a>ASP.NET Core 10
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.AspNetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm)               | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm64)           | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm)     | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm64) | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-x64)     | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-x64)               | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-arm64)               | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-x64)                   | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm)                   | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm64)               | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x64)                   | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107
[Microsoft.AspNetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x86)                   | 10.0.0-rc.1.25451.107 | 10.0.0-rc.2.25502.107

### <a name="ASP.NET Core 9"></a>ASP.NET Core 9
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.AspNetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm)               | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm64)           | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm)     | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm64) | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-x64)     | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-x64)               | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-arm64)               | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-x64)                   | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm)                   | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm64)               | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x64)                   | >= 9.0.0, <= 9.0.9 | 9.0.10
[Microsoft.AspNetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x86)                   | >= 9.0.0, <= 9.0.9 | 9.0.10


### <a name="ASP.NET Core 8"></a>ASP.NET Core 8
Package name | Affected version | Patched version
------------ | ---------------- | -------------------------
[Microsoft.AspNetCore.App.Runtime.linux-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm)               | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.linux-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-arm64)           | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm)     | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.linux-musl-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-arm64) | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.linux-musl-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-musl-x64)     | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.linux-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.linux-x64)               | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.osx-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-arm64)               | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.osx-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.osx-x64)                   | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.win-arm](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm)                   | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.win-arm64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-arm64)               | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.win-x64](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x64)                   | >= 8.0.0, <= 8.0.20 | 8.0.21
[Microsoft.AspNetCore.App.Runtime.win-x86](https://www.nuget.org/packages/Microsoft.AspNetCore.App.Runtime.win-x86)                   | >= 8.0.0, <= 8.0.20 | 8.0.21

## Advisory FAQ

### <a name="how-affected"></a>How do I know if I am affected?

If you have a runtime or SDK with a version listed, or an affected package listed in [affected software](#affected-packages) or [affected packages](#affected-software), you're exposed to the vulnerability.

### <a name="how-fix"></a>How do I fix the issue?

1. To fix the issue please install the latest version of .NET 9.0 and .NET 8.0. If you have installed one or more .NET SDKs through Visual Studio, Visual Studio will prompt you to update Visual Studio, which will also update your .NET  SDKs.
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

* If you're using .NET 8.0, you should download and install .NET 8.0.21  Runtime or .NET 8.0.318 SDK (for Visual Studio 2022 v17.10 latest update) from https://dotnet.microsoft.com/download/dotnet-core/8.0.
* If you're using .NET 9.0, you should download and install .NET 9.0.10  Runtime or .NET 9.0.111 SDK (for Visual Studio 2022 v17.12 latest update) from https://dotnet.microsoft.com/download/dotnet-core/9.0.
* If you're using .NET 10.0, you should download and install .NET 10.0.0-rc.2.25476.107 Runtime or .NET 10.0.100-rc.2.25476.107 SDK (for Visual Studio 2022 v17.12 latest update) from https://dotnet.microsoft.com/download/dotnet-core/10.0.
* If you're using [Microsoft.AspNetCore.Server.Kestrel.Core](https://www.nuget.org/packages/Microsoft.AspNetCore.Server.Kestrel.Core) nuget package, update to the latest version 2.3.6 using either of the following methods:

    * Using the NuGet Package Manager UI in Visual Studio:
            - Open your project in Visual Studio.
            - Right-click on your project in Solution Explorer and select "Manage NuGet Packages..." or navigate to "Project > Manage NuGet Packages".
            - In the NuGet Package Manager window, select the "Updates" tab. This tab lists packages with available updates from your configured package sources.
            - Select the package(s) you wish to update. You can choose a specific version from the dropdown or update to the latest available version.
            - Click the "Update" button.

    * Using the NuGet Package Manager Console in Visual Studio:
            - Open your project in Visual Studio.
            - Navigate to "Tools > NuGet Package Manager > Package Manager Console".
            - To update a specific package to its latest version, use the Update-Package command:
                Code:

                Update-Package -Id Microsoft.AspNetCore.Server.Kestrel.Core

    * Using the .NET CLI (Command Line Interface):
            Open a terminal or command prompt in your project's directory.
            To update a specific package to its latest version:
                Code:

                dotnet add package Microsoft.AspNetCore.Server.Kestrel.Core

Once you have installed the updated runtime or SDK, restart your apps for the update to take effect.

Additionally, if you've deployed [self-contained applications](https://docs.microsoft.com/dotnet/core/deploying/#self-contained-deployments-scd) targeting any of the impacted versions, these applications are also vulnerable and must be recompiled and redeployed.

## Other Information

### Reporting Security Issues

If you have found a potential security issue in .NET 8.0, .NET 9.0 or .NET 10.0, please email details to secure@microsoft.com. Reports may qualify for the Microsoft .NET Core & .NET 5 Bounty. Details of the Microsoft .NET Bounty Program including terms and conditions are at <https://aka.ms/corebounty>.

### Support

You can ask questions about this issue on GitHub in the .NET GitHub organization. The main repos are located at https://github.com/dotnet/aspnetcore. The Announcements repo (https://github.com/dotnet/Announcements) will contain this bulletin as an issue and will include a link to a discussion issue. You can ask questions in the linked discussion issue.

### Disclaimer

The information provided in this advisory is provided "as is" without warranty of any kind. Microsoft disclaims all warranties, either express or implied, including the warranties of merchantability and fitness for a particular purpose. In no event shall Microsoft Corporation or its suppliers be liable for any damages whatsoever including direct, indirect, incidental, consequential, loss of business profits or special damages, even if Microsoft Corporation or its suppliers have been advised of the possibility of such damages. Some states do not allow the exclusion or limitation of liability for consequential or incidental damages so the foregoing limitation may not apply.
### External Links

### Acknowledgement
Sid

[CVE-2025-55315]( https://www.cve.org/CVERecord?id=CVE-2025-55315)

### Revisions

V1.0 (October 14, 2025): Advisory published.

_Version 1.0_

_Last Updated 2025-10-14_

## References
- https://github.com/dotnet/aspnetcore/security/advisories/GHSA-5rrx-jjjq-q2r5
- https://nvd.nist.gov/vuln/detail/CVE-2025-55315
- https://github.com/dotnet/announcements/issues/371
- https://github.com/dotnet/aspnetcore
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-55315
