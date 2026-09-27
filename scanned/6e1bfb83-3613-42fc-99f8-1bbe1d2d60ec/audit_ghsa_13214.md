# [M] graphql Uncontrolled Resource Consumption vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9pv7-vfvm-6vr7
CVE: CVE-2023-26144
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-9pv7-vfvm-6vr7
Type: github-advisory

## Affected
- npm: `graphql` — affected >=16.3.0 <16.8.1

## Details
Versions of the package graphql from 16.3.0 and before 16.8.1 are vulnerable to Denial of Service (DoS) due to insufficient checks in the OverlappingFieldsCanBeMergedRule.ts file when parsing large queries. This vulnerability allows an attacker to degrade system performance.

**Note:** It was not proven that this vulnerability can crash the process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26144
- https://github.com/graphql/graphql-js/issues/3955
- https://github.com/graphql/graphql-js/pull/3972
- https://github.com/graphql/graphql-js/commit/8f4c64eb6a7112a929ffeef00caa67529b3f2fcf
- https://github.com/graphql/graphql-js
- https://github.com/graphql/graphql-js/releases/tag/v16.8.1
- https://security.snyk.io/vuln/SNYK-JS-GRAPHQL-5905181
