# [C] npm package rfc6902 vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-p495-jxh2-wrfg
CVE: CVE-2021-4245
CWE: CWE-1321, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-15
Source: https://github.com/advisories/GHSA-p495-jxh2-wrfg
Type: github-advisory

## Affected
- npm: `rfc6902` — affected >=0 <5.0.0

## Details
A vulnerability classified as problematic has been found in chbrown rfc6902. This affects an unknown part of the file pointer.ts. The manipulation leads to improperly controlled modification of object prototype attributes ('prototype pollution'). The exploit has been disclosed to the public and may be used. The name of the patch is c006ce9faa43d31edb34924f1df7b79c137096cf. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-215883.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4245
- https://github.com/chbrown/rfc6902/issues/84
- https://github.com/chbrown/rfc6902/pull/76
- https://github.com/chbrown/rfc6902/commit/c006ce9faa43d31edb34924f1df7b79c137096cf
- https://github.com/chbrown/rfc6902
- https://vuldb.com/?id.215883
