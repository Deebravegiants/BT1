# [M] HTML Injection in shout

## Summary
Severity: Medium
Advisory: GHSA-26q7-g57v-mxcp
CVE: CVE-2017-16043
CWE: CWE-80
Ecosystem: npm
Published: 2018-11-07
Source: https://github.com/advisories/GHSA-26q7-g57v-mxcp
Type: github-advisory

## Affected
- npm: `shout` — affected >=0.44.0 <0.50.0

## Details
Affected versions of `shout` do not escape the `/topic` command in messages, and are therefore vulnerable to cross-site scripting.


## Recommendation

Update to version 0.50.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16043
- https://github.com/erming/shout/pull/344
- https://github.com/advisories/GHSA-26q7-g57v-mxcp
- https://www.npmjs.com/advisories/322
