# [C] False-positive validity for NFT1 genesis transactions

## Summary
Severity: Critical
Advisory: GHSA-6jmr-jfh7-xg3h
CVE: CVE-2020-15131
CWE: CWE-697
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-07-30
Source: https://github.com/advisories/GHSA-6jmr-jfh7-xg3h
Type: github-advisory

## Affected
- npm: `slp-validate` — affected >=0 <1.2.2

## Details
### Impact
In the npm package named "slp-validate", versions prior to 1.2.2 are vulnerable to false-positive validation outcomes for the NFT1 Child Genesis transaction type. A poorly implemented SLP wallet or opportunistic attacker could create a seemingly valid NFT1 child token without burning any of the NFT1 Group token type as is required by the NFT1 specification.

### Patches
npm package "slp-validate" has been patched and is published and tagged as version 1.2.2.

### Workarounds
Upgrade to slp-validate 1.2.2.

### References
* Package location: https://www.npmjs.com/package/slp-validate
* SLP NFT1 spec: https://slp.dev/specs/slp-nft-1/#nft1-protocol-requirements
* Git commit hash fixing this issue: https://github.com/simpleledger/slp-validate.js/commit/3963cf914afae69084059b82483da916d97af65c
* Unit tests have been added to assist validator implementations in avoiding this bug: https://github.com/simpleledger/slp-unit-test-data/commit/8c942eacfae12686dcf1f3366321445a4fba73e7

### For more information
If you have any questions or comments about this advisory please open an issue in the [slp-validate](https://github.com/simpleledger/slp-validate.js/issues) repository.

## References
- https://github.com/simpleledger/slp-validate.js/security/advisories/GHSA-6jmr-jfh7-xg3h
- https://nvd.nist.gov/vuln/detail/CVE-2020-15131
- https://github.com/simpleledger/slp-validate.js/commit/3963cf914afae69084059b82483da916d97af65c
