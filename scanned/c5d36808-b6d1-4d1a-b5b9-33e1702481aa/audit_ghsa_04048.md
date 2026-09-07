# [M] Cross-Site Scripting in shave

## Summary
Severity: Medium
Advisory: GHSA-gh4g-3gm9-5wrq
CVE: CVE-2019-12313
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-05-29
Source: https://github.com/advisories/GHSA-gh4g-3gm9-5wrq
Type: github-advisory

## Affected
- npm: `shave` — affected >=0 <2.5.3

## Details
Versions of `shave` prior to 2.5.3 are vulnerable to Cross-Site Scripting. The `shave` package overwrites HTML elements and in doing so fails to properly encode the output. If encoded HTML input is passed into `shave` the output will be decoded which may lead to Cross-Site Scripting.


## Recommendation

Upgrade to version 2.5.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12313
- https://github.com/dollarshaveclub/shave/commit/da7371b0531ba14eae48ef1bb1456a3de4cfa954#diff-074799b511e4b61923dfd3f2a3bf9b54R67
- https://github.com/dollarshaveclub/shave/compare/852b537...da7371b
- https://www.npmjs.com/advisories/822
