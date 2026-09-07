# [M] Cross-Site Scripting in buttle

## Summary
Severity: Medium
Advisory: GHSA-pqpp-2363-649v
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-pqpp-2363-649v
Type: github-advisory

## Affected
- npm: `buttle` — affected >=0

## Details
All versions of `buttle` are vulnerable to Cross-Site Scripting. Due to misconfiguration of its rendering engine, `buttle` does not sanitize the HTML output allowing attackers to run arbitrary JavaScript when processing malicious markdown files.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://hackerone.com/reports/404126
- https://www.npmjs.com/advisories/810
