# [C] RSA signature validation vulnerability on maleable encoded message in jsrsasign

## Summary
Severity: Critical
Advisory: GHSA-27fj-mc8w-j9wg
CVE: CVE-2021-30246
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-16
Source: https://github.com/advisories/GHSA-27fj-mc8w-j9wg
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=0 <10.2.0

## Details
### Impact
Vulnerable jsrsasign will accept RSA signature with improper PKCS#1.5 padding.
Decoded RSA signature value consists following form:
`01(ff...(8 or more ffs)...ff)00[ASN.1 OF DigestInfo]`
Its byte length must be the same as RSA key length, however such checking was not sufficient.

To make crafted message for practical attack is very hard.

### Patches
Users validating RSA signature should upgrade to 10.2.0 or later.

### Workarounds
There is no workaround. Not to use RSA signature validation in jsrsasign.

### ACKNOWLEDGEMENT
Thanks to Daniel Yahyazadeh @yahyazadeh for reporting and analyzing this vulnerability.

## References
- https://github.com/kjur/jsrsasign/security/advisories/GHSA-27fj-mc8w-j9wg
- https://nvd.nist.gov/vuln/detail/CVE-2021-30246
- https://github.com/kjur/jsrsasign/issues/478
- https://github.com/kjur/jsrsasign/releases/tag/10.1.13
- https://kjur.github.io/jsrsasign
