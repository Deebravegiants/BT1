# [H] ag-grid Cross-Site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-7p6w-x2gr-rrf8
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-7p6w-x2gr-rrf8
Type: github-advisory

## Affected
- npm: `ag-grid` — affected >=0 <14.0.0

## Details
Versions of `ag-grid` prior to 14.0.0 are vulnerable to Cross-Site Scripting (XSS). Grid contents are not properly sanitized and may allow attackers to execute arbitrary JavaScript if user input is rendered in the grid. 


## Recommendation

Upgrade to version 14.0.0 or later.

## References
- https://github.com/ag-grid/ag-grid/issues/1961
- https://github.com/github/advisory-database/issues/5799
- https://github.com/ag-grid/ag-grid/commit/b66b1ddf73056714f6574e054d6e05d6ba531ce8
- https://github.com/ag-grid/ag-grid
