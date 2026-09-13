# [M] FullStackHero's WebAPI Boilerplate host header injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-75x2-6h4m-h6mx
CVE: CVE-2024-26470
CWE: CWE-200
Ecosystem: NuGet
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-75x2-6h4m-h6mx
Type: github-advisory

## Affected
- NuGet: `FullStackHero.WebAPI.Boilerplate` — affected >=1.0.0

## Details
A host header injection vulnerability in the forgot password function of FullStackHero's WebAPI Boilerplate v1.0.0 and v1.0.1 allows attackers to leak the password reset token via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-26470
- https://github.com/dub-flow/vulnerability-research/tree/main/CVE-2024-26470
- https://github.com/fullstackhero/dotnet-webapi-boilerplate
- https://www.nuget.org/packages/FullStackHero.WebAPI.Boilerplate
