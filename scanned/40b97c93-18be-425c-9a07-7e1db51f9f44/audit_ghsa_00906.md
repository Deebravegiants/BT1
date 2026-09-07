# [H] Cross-Site Scripting in semantic-ui-search

## Summary
Severity: High
Advisory: GHSA-p9vv-3945-x93h
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-p9vv-3945-x93h
Type: github-advisory

## Affected
- npm: `semantic-ui-search` — affected >=0

## Details
All versions of `semantic-ui-search` are vulnerable to Cross-Site Scripting. Lack of output encoding on the selection dropdowns can lead to user input being executed instead of printed as text.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://github.com/Semantic-Org/Semantic-UI/issues/4498
- https://github.com/Semantic-Org/Semantic-UI
- https://www.npmjs.com/advisories/760
