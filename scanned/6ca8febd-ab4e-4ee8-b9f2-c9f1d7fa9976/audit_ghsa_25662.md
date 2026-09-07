# [H] Improper Certificate Validation

## Summary
Severity: High
Advisory: GHSA-7mfr-774f-w5r9
CVE: CVE-2017-11770
CWE: CWE-295
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-7mfr-774f-w5r9
Type: github-advisory

## Affected
- NuGet: `System.Security.Cryptography.X509Certificates` — affected >=4.0.0 <4.1.2
- NuGet: `Microsoft.NETCore.App` — affected >=1.0.0 <2.0.3

## Details
.NET Core 1.0, 1.1, and 2.0 allow an unauthenticated attacker to remotely cause a denial of service attack against a .NET Core web application by improperly parsing certificate data. A denial of service vulnerability exists when .NET Core improperly handles parsing certificate data, aka ".NET CORE Denial Of Service Vulnerability".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11770
- https://access.redhat.com/errata/RHSA-2017:3248
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11770
- http://www.securityfocus.com/bid/101710
- http://www.securitytracker.com/id/1039787
