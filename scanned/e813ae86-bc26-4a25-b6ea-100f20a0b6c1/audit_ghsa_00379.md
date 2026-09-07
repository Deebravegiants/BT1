# [H] Denial of service vulnerability exists when System.IO.Pipelines improperly handles requests

## Summary
Severity: High
Advisory: GHSA-j378-6mmw-hqfr
CVE: CVE-2018-8409
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-j378-6mmw-hqfr
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.All` — affected >=2.1.0 <2.1.4
- NuGet: `Microsoft.AspNetCore.App` — affected >=2.1.0 <2.1.4
- NuGet: `System.IO.Pipelines` — affected >=4.5.0 <4.5.1

## Details
A denial of service vulnerability exists when System.IO.Pipelines improperly handles requests, aka "System.IO.Pipelines Denial of Service." This affects .NET Core 2.1, System.IO.Pipelines, ASP.NET Core 2.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8409
- https://github.com/advisories/GHSA-j378-6mmw-hqfr
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8409
- http://www.securityfocus.com/bid/105223
