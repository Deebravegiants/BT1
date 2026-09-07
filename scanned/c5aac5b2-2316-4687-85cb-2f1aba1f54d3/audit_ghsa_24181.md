# [H] .NET Framework, SharePoint Server, and Visual Studio Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-g5vf-38cp-4px9
CVE: CVE-2020-1147
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g5vf-38cp-4px9
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App` — affected >=2.1.0 <2.1.20
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.rhel.6-x64` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm64` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=3.1.0 <3.1.6
- NuGet: `Microsoft.NETCore.App.Runtime.win-x86` — affected >=3.1.0 <3.1.6

## Details
A remote code execution vulnerability exists in .NET Framework, Microsoft SharePoint, and Visual Studio when the software fails to check the source markup of XML file input, aka '.NET Framework, SharePoint Server, and Visual Studio Remote Code Execution Vulnerability'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1147
- https://github.com/dotnet/announcements/issues/159
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1147
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-1147
- https://www.exploitalert.com/view-details.html?id=35992
- http://packetstormsecurity.com/files/158694/SharePoint-DataSet-DataTable-Deserialization.html
- http://packetstormsecurity.com/files/158876/Microsoft-SharePoint-Server-2019-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/163644/Microsoft-SharePoint-Server-2019-Remote-Code-Execution.html
