# [H] Exposure of Sensitive Information in System.Net.Http

## Summary
Severity: High
Advisory: GHSA-2xjx-v99w-gqf3
CVE: CVE-2019-0545
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2xjx-v99w-gqf3
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App` — affected >=2.1.0 <2.1.7
- NuGet: `Microsoft.NETCore.App` — affected >=2.2.0 <2.2.1

## Details
An information disclosure vulnerability exists in .NET Framework and .NET Core which allows bypassing Cross-origin Resource Sharing (CORS) configurations, aka ".NET Framework Information Disclosure Vulnerability." This affects Microsoft .NET Framework 2.0, Microsoft .NET Framework 3.0, Microsoft .NET Framework 4.6.2/4.7/4.7.1/4.7.2, Microsoft .NET Framework 4.5.2, Microsoft .NET Framework 4.6, Microsoft .NET Framework 4.6/4.6.1/4.6.2/4.7/4.7.1/4.7.2, Microsoft .NET Framework 4.7/4.7.1/4.7.2, .NET Core 2.1, Microsoft .NET Framework 4.7.1/4.7.2, Microsoft .NET Framework 3.5, Microsoft .NET Framework 3.5.1, Microsoft .NET Framework 4.6/4.6.1/4.6.2, .NET Core 2.2, Microsoft .NET Framework 4.7.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0545
- https://github.com/dotnet/announcements/issues/94
- https://access.redhat.com/errata/RHSA-2019:0040
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0545
- http://www.securityfocus.com/bid/106405
