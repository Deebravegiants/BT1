# [C] Critical severity vulnerability that affects slpjs

## Summary
Severity: Critical
Advisory: GHSA-425c-ccf3-3jrr
CVE: CVE-2019-16762
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2019-11-15
Source: https://github.com/advisories/GHSA-425c-ccf3-3jrr
Type: github-advisory

## Affected
- npm: `slpjs` — affected >=0 <0.21.4

## Details
## Validator parsing discrepancy due to string encoding

### Impact
A specially crafted Bitcoin script can cause a discrepancy between the specified SLP consensus rules and the validation result of the slpjs npm package. An attacker could create a specially crafted Bitcoin script in order to cause a hard-fork from the SLP consensus.

### Patches
All versions > 0.21.3 are patched.

### Workarounds
Upgrade to any version >= 0.21.4.

### References
The bug was located and fixed [here](https://github.com/simpleledger/slpjs/commit/ac8809b42e47790a6f0205991b36f2699ed10c84#diff-fe58606994c412ba56a65141a7aa4a62L701).

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [slpjs repo](https://github.com/simpleledger/slpjs/issues)
* Email us at [info@slp.cash](mailto:info@slp.cash)

## References
- https://github.com/simpleledger/slpjs/security/advisories/GHSA-425c-ccf3-3jrr
- https://nvd.nist.gov/vuln/detail/CVE-2019-16762
- https://github.com/simpleledger/slpjs/commit/ac8809b42e47790a6f0205991b36f2699ed10c84#diff-fe58606994c412ba56a65141a7aa4a62L701
- https://github.com/advisories/GHSA-425c-ccf3-3jrr
