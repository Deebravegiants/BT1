# [M] Cross-Site Scripting in webpack-bundle-analyzer

## Summary
Severity: Medium
Advisory: GHSA-pgr8-jg6h-8gw6
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-05-23
Source: https://github.com/advisories/GHSA-pgr8-jg6h-8gw6
Type: github-advisory

## Affected
- npm: `webpack-bundle-analyzer` — affected >=0 <3.3.2

## Details
Versions of `webpack-bundle-analyzer` prior to 3.3.2 are vulnerable to Cross-Site Scripting. The package uses `JSON.stringify()` without properly escaping input which may lead to Cross-Site Scripting.


## Recommendation

Upgrade to version 3.3.2 or later.

## References
- https://github.com/webpack-contrib/webpack-bundle-analyzer/issues/263
- https://github.com/webpack-contrib/webpack-bundle-analyzer/pull/264
- https://github.com/webpack-contrib/webpack-bundle-analyzer/commit/20f2b4c553ee343f491faf63e39427fba9908c7c
- https://snyk.io/vuln/SNYK-JS-WEBPACKBUNDLEANALYZER-174190
- https://www.npmjs.com/advisories/826
