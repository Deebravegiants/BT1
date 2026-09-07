# [H] Open redirect in ASP.NET Core

## Summary
Severity: High
Advisory: GHSA-3wcj-rg8q-9cqv
CVE: CVE-2017-11879
CWE: CWE-601
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3wcj-rg8q-9cqv
Type: github-advisory

## Affected
- NuGet: `Microsoft.AspNetCore.All` — affected >=2.0.0 <2.0.3
- NuGet: `Microsoft.AspNetCore.Mvc.Core` — affected >=2.0.0 <2.0.1

## Details
ASP.NET Core 2.0 allows an attacker to steal log-in session information such as cookies or authentication tokens via a specially crafted URL aka "ASP.NET Core Elevation Of Privilege Vulnerability".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11879
- https://github.com/aspnet/Announcements/issues/277
- https://github.com/github/advisory-database/issues/302
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11879
