# [H] Command Injection in @graphql-tools/git-loader

## Summary
Severity: High
Advisory: GHSA-vhhw-xjvf-wprr
CVE: CVE-2021-23326
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-vhhw-xjvf-wprr
Type: github-advisory

## Affected
- npm: `@graphql-tools/git-loader` — affected >=0 <6.2.6

## Details
This affects the package @graphql-tools/git-loader before 6.2.6. The use of exec and execSync in packages/loaders/git/src/load-git.ts allows arbitrary command injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23326
- https://github.com/ardatan/graphql-tools/pull/2470
- https://github.com/ardatan/graphql-tools/commit/6a966beee8ca8b2f4adfe93318b96e4a5c501eac
- https://advisory.checkmarx.net/advisory/CX-2020-4300
- https://github.com/ardatan/graphql-tools/releases/tag/%40graphql-tools%2Fgit-loader%406.2.6
- https://snyk.io/vuln/SNYK-JS-GRAPHQLTOOLSGITLOADER-1062543
