# [M] Inefficient Regular Expression Complexity in Validator.js

## Summary
Severity: Medium
Advisory: GHSA-xx4c-jj58-r7x6
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-xx4c-jj58-r7x6
Type: github-advisory

## Affected
- npm: `validator` — affected >=11.1.0 <13.7.0

## Details
### Impact
Versions of `validator` prior to 13.7.0 are affected by an inefficient Regular Expression complexity  when using the `rtrim` and `trim` sanitizers.

### Patches
The problem has been patched in validator 13.7.0

## References
- https://github.com/validatorjs/validator.js/security/advisories/GHSA-xx4c-jj58-r7x6
- https://nvd.nist.gov/vuln/detail/CVE-2021-3765
- https://github.com/validatorjs/validator.js/issues/1599
- https://github.com/validatorjs/validator.js/pull/1738
- https://github.com/validatorjs/validator.js
- https://huntr.dev/bounties/c37e975c-21a3-4c5f-9b57-04d63b28cfc9
