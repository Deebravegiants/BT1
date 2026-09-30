# [H] Denial of service in ASP.NET Core

## Summary
Severity: High
Advisory: GHSA-mv2r-q4g5-j8q5
CVE: CVE-2018-8269
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-mv2r-q4g5-j8q5
Type: github-advisory

## Affected
- NuGet: `Microsoft.Data.OData` — affected >=0 <5.8.4
- NuGet: `Microsoft.AspNetCore.DataProtection.AzureStorage` — affected >=2.1.0 <2.1.13
- NuGet: `Microsoft.AspNetCore.DataProtection.AzureStorage` — affected >=2.2.0 <2.2.7
- NuGet: `Microsoft.AspNetCore.All` — affected >=2.1.0 <2.1.13
- NuGet: `Microsoft.AspNetCore.All` — affected >=2.2.0 <2.2.7

## Details
A denial of service vulnerability exists when OData Library improperly handles web requests, aka "OData Denial of Service Vulnerability." This affects Microsoft.Data.OData.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8269
- https://github.com/aspnet/Announcements/issues/385
- https://github.com/github/advisory-database/issues/302
- https://github.com/advisories/GHSA-mv2r-q4g5-j8q5
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8269
- https://www.exploit-db.com/exploits/46101
