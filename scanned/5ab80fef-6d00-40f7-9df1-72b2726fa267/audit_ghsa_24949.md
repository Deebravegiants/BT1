# [H] .NET Core Denial of Service Vulnerability

## Summary
Severity: High
Advisory: GHSA-xcvr-qv8h-m7xw
CVE: CVE-2018-0875
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xcvr-qv8h-m7xw
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.Jit` — affected >=2.0.0 <2.0.6
- NuGet: `Microsoft.NETCore.Jit` — affected >=1.1.0 <1.1.7
- NuGet: `Microsoft.NETCore.Jit` — affected >=0 <1.0.12

## Details
.NET Core 1.0, .NET Core 1.1, NET Core 2.0 and PowerShell Core 6.0.0 allow a denial of Service vulnerability due to how specially crafted requests are handled, aka ".NET Core Denial of Service Vulnerability".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0875
- https://github.com/dotnet/announcements/issues/62
- https://access.redhat.com/errata/RHSA-2018:0522
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-0875
- http://www.securityfocus.com/bid/103225
- http://www.securitytracker.com/id/1040505
