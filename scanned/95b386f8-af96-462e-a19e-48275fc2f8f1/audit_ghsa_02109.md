# [M] Signature validation bypass in ServiceStack

## Summary
Severity: Medium
Advisory: GHSA-v5rv-hpxg-8x49
CVE: CVE-2020-28042
CWE: CWE-347
Ecosystem: NuGet
Published: 2021-01-13
Source: https://github.com/advisories/GHSA-v5rv-hpxg-8x49
Type: github-advisory

## Affected
- NuGet: `ServiceStack` — affected >=0 <5.9.2

## Details
ServiceStack before 5.9.2 mishandles JWT signature verification unless an application has a custom ValidateToken function that establishes a valid minimum length for a signature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28042
- https://github.com/ServiceStack/ServiceStack/commit/540d4060e877a03ae95343c1a8560a26768585ee
- https://forums.servicestack.net/t/servicestack-v5-9-2-released/8850
- https://snyk.io/vuln/SNYK-DOTNET-SERVICESTACK-1035519
- https://www.nuget.org/packages/ServiceStack
- https://www.shielder.it/advisories/servicestack-jwt-signature-verification-bypass
- https://www.shielder.it/blog/2020/11/re-discovering-a-jwt-authentication-bypass-in-servicestack
