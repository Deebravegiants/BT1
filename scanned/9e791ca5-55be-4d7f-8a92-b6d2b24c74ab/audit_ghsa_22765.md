# [M] Tampering vulnerability in .NET Core

## Summary
Severity: Medium
Advisory: GHSA-5633-f33j-c6f7
CVE: CVE-2018-8416
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5633-f33j-c6f7
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App` — affected >=2.1.0 <2.1.7

## Details
A tampering vulnerability exists when .NET Core improperly handles specially crafted files, aka ".NET Core Tampering Vulnerability." This affects .NET Core 2.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8416
- https://github.com/dotnet/announcements/issues/95
- https://github.com/github/advisory-database/issues/302
- https://access.redhat.com/errata/RHSA-2018:3676
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8416
