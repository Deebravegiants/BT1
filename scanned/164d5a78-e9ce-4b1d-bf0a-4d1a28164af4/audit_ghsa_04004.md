# [H] No CSRF Validation in droppy

## Summary
Severity: High
Advisory: GHSA-rhvc-x32h-5526
CVE: CVE-2016-10529
CWE: CWE-352
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-rhvc-x32h-5526
Type: github-advisory

## Affected
- npm: `droppy` — affected >=0 <3.5.0

## Details
Affected versions of `droppy`  are vulnerable to cross-site socket forgery. The package does not perform verification for cross-domain websocket requests, and as a result, an attacker can create a web page that opens up a websocket connection on behalf of the user visiting the page. The attacker can then perform any action that the target user could, including adding a new admin account under their control, or deleting others.


## Recommendation

Update to version 3.5.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10529
- https://github.com/advisories/GHSA-rhvc-x32h-5526
- https://www.npmjs.com/advisories/91
