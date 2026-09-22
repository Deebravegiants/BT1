# [H] Prototype Pollution in @apollo/gateway

## Summary
Severity: High
Advisory: GHSA-74cr-77xc-8g6r
CWE: CWE-1321, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-74cr-77xc-8g6r
Type: github-advisory

## Affected
- npm: `@apollo/gateway` — affected >=0 <0.6.2

## Details
Versions of `@apollo/gateway` prior to 0.6.2 are vulnerable to Prototype Pollution. The package uses deepMerge() to merge objects, which may allow attackers to alter the Object prototype through queries with GraphQL aliases. Carefully constructed payloads can override properties of all objects in the application. This may lead to Denial of Service or may be chained with other vulnerabilities leading to Remote Code Execution.


## Recommendation

Upgrade to version 0.6.2 or later.

## References
- https://github.com/apollographql/apollo-server/pull/2779
- https://github.com/apollographql/apollo-server/commit/cea7397582a293af6a5f60947da34b95e669c6c1
- https://snyk.io/vuln/SNYK-JS-APOLLOGATEWAY-174915
- https://www.npmjs.com/advisories/917
