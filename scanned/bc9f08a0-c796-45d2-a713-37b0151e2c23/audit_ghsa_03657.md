# [M] Denial of Service in canvas

## Summary
Severity: Medium
Advisory: GHSA-vpq5-4rc8-c222
Ecosystem: npm
Published: 2019-06-05
Source: https://github.com/advisories/GHSA-vpq5-4rc8-c222
Type: github-advisory

## Affected
- npm: `canvas` — affected >=0 <1.6.10

## Details
Versions of `canvas` prior to 1.6.10 are vulnerable to Denial of Service. Processing malicious JPEGs or GIFs could crash the node process.


## Recommendation

Upgrade to version 1.6.10

## References
- https://github.com/Automattic/node-canvas/commit/c3e4ccb1c404da01e83fe5eb3626bf55f7f55957
- https://hackerone.com/reports/315037
- https://www.npmjs.com/advisories/804
