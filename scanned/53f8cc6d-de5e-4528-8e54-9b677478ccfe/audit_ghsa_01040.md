# [H] Path Traversal in ponse

## Summary
Severity: High
Advisory: GHSA-wfhx-6pcm-7m55
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-wfhx-6pcm-7m55
Type: github-advisory

## Affected
- npm: `ponse` — affected >=0 <2.0.2

## Details
Versions of `ponse` prior to 2.0.2 are vulnerable to Path Traversal. The package fails to sanitize URLs, allowing attackers to access server files outside of the served folder using relative paths.


## Recommendation

Upgrade to version 2.0.2 or later.

## References
- https://hackerone.com/reports/383112
- https://www.npmjs.com/advisories/1002
