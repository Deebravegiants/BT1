# [M] Insecure Default Configuration in airbrake

## Summary
Severity: Medium
Advisory: GHSA-856x-cp3q-47vg
CVE: CVE-2016-10530
CWE: CWE-200
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-856x-cp3q-47vg
Type: github-advisory

## Affected
- npm: `airbrake` — affected >=0 <0.4.0

## Details
Affected versions of `airbrake` default to sending environment variables over an unencrypted HTTP connection. In scenarios where an attacker has a privileged network position, it is possible for them to capture and read these environment variables, which may result in leaking sensitive information.


## Recommendation

Update to version 0.4.0 or later, or upgrade from the now-deprecated `airbrake` module to its replacement, [`airbrake-js`](https://www.npmjs.com/package/airbrake-js).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10530
- https://github.com/airbrake/node-airbrake/issues/70
- https://github.com/advisories/GHSA-856x-cp3q-47vg
- https://www.npmjs.com/advisories/96
