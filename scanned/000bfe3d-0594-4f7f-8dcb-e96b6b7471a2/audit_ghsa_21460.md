# [M] deep-object-diff vulnerable to Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-653v-rqx9-j85p
CVE: CVE-2022-41713
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-04
Source: https://github.com/advisories/GHSA-653v-rqx9-j85p
Type: github-advisory

## Affected
- npm: `deep-object-diff` — affected >=1.1.6 <1.1.9

## Details
deep-object-diff before version 1.1.6 allows an external attacker to edit or add new properties to an object. This is possible because the application does not properly validate incoming JSON keys, thus allowing the `__proto__` property to be edited. This issue was fixed in version 1.1.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41713
- https://github.com/mattphillips/deep-object-diff/issues/85
- https://github.com/mattphillips/deep-object-diff/issues/85#issuecomment-1312450353
- https://github.com/mattphillips/deep-object-diff/pull/87/commits/55f9c3c70cf0d54cb30291e949fb8682fa3c5d9f
- https://github.com/mattphillips/deep-object-diff/pull/87/commits/9576963b68b955e88610aa4f0c696a1aafc1119d
- https://fluidattacks.com/advisories/heldens
- https://github.com/mattphillips/deep-object-diff
