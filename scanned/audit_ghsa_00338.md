# [H] Improper Certificate Validation in Microsoft .NET Framework components

## Summary
Severity: High
Advisory: GHSA-jc8g-xhw5-6x46
CVE: CVE-2018-0786
CWE: CWE-295
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-jc8g-xhw5-6x46
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.UniversalWindowsPlatform` — affected >=5.2.0 <5.2.4
- NuGet: `Microsoft.NETCore.UniversalWindowsPlatform` — affected >=5.3.0 <5.3.5
- NuGet: `Microsoft.NETCore.UniversalWindowsPlatform` — affected >=5.4.0 <5.4.2
- NuGet: `Microsoft.NETCore.UniversalWindowsPlatform` — affected >=6.0.0 <6.0.6
- NuGet: `System.ServiceModel.Primitives` — affected >=4.4.0 <4.4.1
- NuGet: `System.ServiceModel.Primitives` — affected >=4.3.0 <4.3.1
- NuGet: `System.ServiceModel.Primitives` — affected >=4.1.0 <4.1.1
- NuGet: `System.ServiceModel.Http` — affected >=4.4.0 <4.4.1
- NuGet: `System.ServiceModel.Http` — affected >=4.3.0 <4.3.1
- NuGet: `System.ServiceModel.Http` — affected >=4.1.0 <4.1.1
- NuGet: `System.ServiceModel.NetTcp` — affected >=4.4.0 <4.4.1
- NuGet: `System.ServiceModel.NetTcp` — affected >=4.3.0 <4.3.1
- NuGet: `System.ServiceModel.NetTcp` — affected >=4.1.0 <4.1.1
- NuGet: `System.ServiceModel.Duplex` — affected >=4.4.0 <4.4.1
- NuGet: `System.ServiceModel.Duplex` — affected >=4.3.0 <4.3.1
- NuGet: `System.ServiceModel.Duplex` — affected >=4.0.1 <4.0.2
- NuGet: `System.ServiceModel.Security` — affected >=4.4.0 <4.4.1
- NuGet: `System.ServiceModel.Security` — affected >=4.3.0 <4.3.1
- NuGet: `System.ServiceModel.Security` — affected >=4.0.1 <4.0.2
- NuGet: `System.Private.ServiceModel` — affected >=4.4.0 <4.4.1
- NuGet: `System.Private.ServiceModel` — affected >=4.3.0 <4.3.1
- NuGet: `System.Private.ServiceModel` — affected >=4.1.0 <4.1.1

## Details
Microsoft .NET Framework 2.0 SP2, 3.0 SP2, 3.5, 3.5.1, 4.5.2, 4.6, 4.6.1, 4.6.2, 4.7, 4.7.1, .NET Core 1.0 and 2.0, and PowerShell Core 6.0.0 allow a security feature bypass vulnerability due to the way certificates are validated, aka ".NET Security Feature Bypass Vulnerability."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0786
- https://github.com/dotnet/announcements/issues/51
- https://github.com/github/advisory-database/issues/302
- https://github.com/advisories/GHSA-jc8g-xhw5-6x46
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0786
- https://www.nuget.org/packages/System.ServiceModel.Duplex#versions-body-tab
