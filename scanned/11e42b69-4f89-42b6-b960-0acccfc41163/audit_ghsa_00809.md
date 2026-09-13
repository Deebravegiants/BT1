# [C] Command Injection in ungit

## Summary
Severity: Critical
Advisory: GHSA-vjfr-p6hp-jqqw
CVE: CVE-2015-4130
CWE: CWE-77
Ecosystem: npm
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-vjfr-p6hp-jqqw
Type: github-advisory

## Affected
- npm: `ungit` — affected >=0 <0.9.0

## Details
Versions of `ungit` prior to 0.9.0 are affected by a command injection vulnerability in the `url` parameter.


## Recommendation

Update version 0.9.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-4130
- https://github.com/FredrikNoren/ungit/issues/486
- https://github.com/FredrikNoren/ungit
- https://www.npmjs.com/advisories/40
