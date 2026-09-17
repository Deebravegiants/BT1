# [H] robots-txt-guard Inefficient Regular Expression Complexity vulnerability

## Summary
Severity: High
Advisory: GHSA-6g33-8w2q-4hxv
CVE: CVE-2021-4305
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-6g33-8w2q-4hxv
Type: github-advisory

## Affected
- npm: `robots-txt-guard` — affected >=0 <1.0.2

## Details
A vulnerability was found in Woorank robots-txt-guard. It has been rated as problematic. Affected by this issue is the function makePathPattern of the file lib/patterns.js. The manipulation of the argument pattern leads to inefficient regular expression complexity. The exploit has been disclosed to the public and may be used. The name of the patch is c03827cd2f9933619c23894ce7c98401ea824020. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-217448.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4305
- https://github.com/Woorank/robots-txt-guard/pull/4
- https://github.com/Woorank/robots-txt-guard/commit/c03827cd2f9933619c23894ce7c98401ea824020
- https://github.com/Woorank/robots-txt-guard
- https://vuldb.com/?ctiid.217448
- https://vuldb.com/?id.217448
