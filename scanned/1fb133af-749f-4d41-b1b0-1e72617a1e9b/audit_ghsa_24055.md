# [M] Improper Input Validation in .Net Framework API's

## Summary
Severity: Medium
Advisory: GHSA-x5qj-9vmx-7g6g
CVE: CVE-2019-0657
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x5qj-9vmx-7g6g
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App` — affected >=2.2.0 <2.2.2
- NuGet: `Microsoft.NETCore.App` — affected >=2.1.0 <2.1.8
- NuGet: `System.Private.Uri` — affected >=4.3.0 <4.3.2

## Details
A vulnerability exists in certain .Net Framework API's and Visual Studio in the way they parse URL's, aka '.NET Framework and Visual Studio Spoofing Vulnerability'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0657
- https://github.com/dotnet/announcements/issues/97
- https://github.com/github/advisory-database/issues/302
- https://access.redhat.com/errata/RHSA-2019:0349
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0657
- http://www.securityfocus.com/bid/106890
