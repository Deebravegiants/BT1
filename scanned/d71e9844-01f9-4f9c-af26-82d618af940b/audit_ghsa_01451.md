# [M] Unauthorized File Access in glance

## Summary
Severity: Medium
Advisory: GHSA-vw7g-jq9m-3q9v
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-vw7g-jq9m-3q9v
Type: github-advisory

## Affected
- npm: `glance` — affected >=0 <3.0.7

## Details
Versions of `glance` prior to 3.0.7 are vulnerable to Unauthorized File Access. The package provides a `--nodot` option meant to hide files and directories with names that begin with a `.`, such as `.git` but fails to hide files inside a folder that begins with `.`. 


## Recommendation

Upgrade to version 3.0.7 or later.

## References
- https://hackerone.com/reports/490379
- https://www.npmjs.com/advisories/811
