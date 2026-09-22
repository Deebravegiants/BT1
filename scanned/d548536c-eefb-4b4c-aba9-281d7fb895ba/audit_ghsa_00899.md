# [C] Command Injection in gm

## Summary
Severity: Critical
Advisory: GHSA-pjh3-jv7w-9jpr
CVE: CVE-2015-7982
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-pjh3-jv7w-9jpr
Type: github-advisory

## Affected
- npm: `gm` — affected >=0 <1.21.1

## Details
Versions of `gm` prior to 1.21.1 are affected by a command injection vulnerability. The vulnerability is triggered when user input is passed into `gm.compare()`, which fails to sanitize input correctly before calling the graphics magic binary.


## Recommendation

Update to version 1.21.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7982
- https://github.com/aheckmann/gm/commit/5f5c77490aa84ed313405c88905eb4566135be31
- https://github.com/aheckmann/gm
- https://www.npmjs.com/advisories/54
