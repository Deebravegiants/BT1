# [H] Improper Input Validation in Microsoft.NETCore.App

## Summary
Severity: High
Advisory: GHSA-8884-xcr4-r68p
CVE: CVE-2017-8585
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-8884-xcr4-r68p
Type: github-advisory

## Affected
- NuGet: `Microsoft.NETCore.App` — affected >=1.0.0 <1.0.7
- NuGet: `Microsoft.NETCore.App` — affected >=1.1.0 <1.1.4

## Details
Microsoft .NET Framework 4.6, 4.6.1, 4.6.2, and 4.7 allow an attacker to send specially crafted requests to a .NET web application, resulting in denial of service, aka .NET Denial of Service Vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8585
- https://github.com/dotnet/corefx/issues/24703
- https://access.redhat.com/errata/RHSA-2017:3248
- https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2017-8585
- http://www.securityfocus.com/bid/99432
- http://www.securitytracker.com/id/1038864
