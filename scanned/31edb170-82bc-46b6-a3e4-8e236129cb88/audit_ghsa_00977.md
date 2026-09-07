# [M] Cross-Site Scripting in diagram-js-direct-editing

## Summary
Severity: Medium
Advisory: GHSA-j8r2-2x94-2q67
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-j8r2-2x94-2q67
Type: github-advisory

## Affected
- npm: `diagram-js-direct-editing` — affected >=0 <1.4.3

## Details
Versions of `diagram-js-direct-editing` prior to 1.4.3 are vulnerable to Cross-Site Scripting. The package fails to sanitize input from the clipboard, allowing attackers to execute arbitrary JavaScript in the victim's browser.


## Recommendation

Upgrade to version 1.4.3 or later.

## References
- https://github.com/bpmn-io/diagram-js-direct-editing
- https://www.npmjs.com/advisories/983
