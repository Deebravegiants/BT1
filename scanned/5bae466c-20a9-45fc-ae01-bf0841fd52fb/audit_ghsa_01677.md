# [C] False-negative validation results in MINT transactions with invalid baton

## Summary
Severity: Critical
Advisory: GHSA-4w97-57v2-3w44
CVE: CVE-2020-11072
CWE: CWE-697
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-05-12
Source: https://github.com/advisories/GHSA-4w97-57v2-3w44
Type: github-advisory

## Affected
- npm: `slp-validate` — affected >=0 <1.2.1

## Details
### Impact
Users could experience false-negative validation outcomes for [MINT](https://github.com/simpleledger/slp-specifications/blob/master/slp-token-type-1.md#mint---extended-minting-transaction) transaction operations.  A poorly implemented SLP wallet could allow spending of the affected tokens which would result in the destruction of a user's minting baton.

### Patches
npm package [slp-validate](https://www.npmjs.com/package/slp-validate) has been patched and published as version 1.2.1.

### Workarounds
Upgrade to slp-validate 1.2.1.

### References
* slp-validate [commit](https://github.com/simpleledger/slp-validate/commit/cde95c0c6470dceb4f023cd462f904135ebd73e7)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [slp-validate](https://github.com/simpleledger/slp-validate/issues)

## References
- https://github.com/simpleledger/slp-validate.js/security/advisories/GHSA-4w97-57v2-3w44
- https://github.com/simpleledger/slp-validate/security/advisories/GHSA-4w97-57v2-3w44
- https://nvd.nist.gov/vuln/detail/CVE-2020-11072
- https://github.com/simpleledger/slp-validate/commit/cde95c0c6470dceb4f023cd462f904135ebd73e7
