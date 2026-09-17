# [C] Validation Bypass in slp-validate

## Summary
Severity: Critical
Advisory: GHSA-wmx6-vxcf-c3gr
CVE: CVE-2019-16761
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2019-11-15
Source: https://github.com/advisories/GHSA-wmx6-vxcf-c3gr
Type: github-advisory

## Affected
- npm: `slp-validate` — affected >=1.0.0 <1.0.1

## Details
Versions of `slp-validate` prior to 1.0.1 are vulnerable to a validation bypass. Bitcoin scripts may cause the validation result from `slp-validate` to differ from the specified SLP consensus. This allows an attacker to create a Bitcoin script that causes a hard-fork from the SLP consensus.


## Recommendation

Upgrade to version 1.0.1 or later.

## References
- https://github.com/simpleledger/slp-validate/security/advisories/GHSA-wmx6-vxcf-c3gr
- https://nvd.nist.gov/vuln/detail/CVE-2019-16761
- https://github.com/simpleledger/slp-validate/commit/50ad96c2798dad6b9f9a13333dd05232defe5730#diff-fe58606994c412ba56a65141a7aa4a62L123
- https://github.com/advisories/GHSA-wmx6-vxcf-c3gr
- https://www.npmjs.com/advisories/1422
