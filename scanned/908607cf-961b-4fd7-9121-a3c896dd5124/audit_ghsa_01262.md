# [M] Cross-Site Scripting in google-closure-library

## Summary
Severity: Medium
Advisory: GHSA-r9q4-w3fm-wrm2
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-r9q4-w3fm-wrm2
Type: github-advisory

## Affected
- npm: `google-closure-library` — affected >=0 <20190301.0.0

## Details
Versions of `google-closure-library` prior to 20190301.0.0 are vulnerable to Cross-Site Scripting. The `safedomtreeprocessor.processToString()` function improperly processed empty elements, which could allow attackers to execute arbitrary JavaScript through Mutation Cross-Site Scripting.


## Recommendation

Upgrade to version 20190301.0.0 or later.

## References
- https://github.com/google/closure-library/commit/c79ab48e8e962fee57e68739c00e16b9934c0ffa#commitcomment-33294853
- https://github.com/google/closure-library
- https://snyk.io/vuln/SNYK-JS-GOOGLECLOSURELIBRARY-174519
- https://www.npmjs.com/advisories/878
