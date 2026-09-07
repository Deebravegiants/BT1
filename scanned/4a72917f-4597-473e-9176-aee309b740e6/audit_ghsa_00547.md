# [C] Critical severity vulnerability that affects recurly-api-client

## Summary
Severity: Critical
Advisory: GHSA-xpwp-rq3x-x6v7
CVE: CVE-2017-0907
CWE: CWE-918
Ecosystem: NuGet
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-xpwp-rq3x-x6v7
Type: github-advisory

## Affected
- NuGet: `recurly-api-client` — affected >=0 <1.0.1
- NuGet: `recurly-api-client` — affected >=1.1.0 <1.1.10
- NuGet: `recurly-api-client` — affected >=1.2.0 <1.2.8
- NuGet: `recurly-api-client` — affected >=1.3.0 <1.3.2
- NuGet: `recurly-api-client` — affected >=1.4.0 <1.4.14
- NuGet: `recurly-api-client` — affected >=1.5.0 <1.5.3
- NuGet: `recurly-api-client` — affected >=1.6.0 <1.6.2
- NuGet: `recurly-api-client` — affected >=1.7.0 <1.7.1
- NuGet: `recurly-api-client` — affected >=1.8.0 <1.8.1

## Details
The Recurly Client .NET Library before 1.0.1, 1.1.10, 1.2.8, 1.3.2, 1.4.14, 1.5.3, 1.6.2, 1.7.1, 1.8.1 is vulnerable to a Server-Side Request Forgery vulnerability due to incorrect use of "Uri.EscapeUriString" that could result in compromise of API keys or other critical resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0907
- https://github.com/recurly/recurly-client-net/commit/9eef460c0084afd5c24d66220c8b7a381cf9a1f1
- https://hackerone.com/reports/288635
- https://dev.recurly.com/page/net-updates
- https://github.com/advisories/GHSA-xpwp-rq3x-x6v7
