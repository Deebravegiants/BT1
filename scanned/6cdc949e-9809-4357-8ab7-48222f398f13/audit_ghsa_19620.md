# [M] GeSHi XSS possible in the get_var function of /contrib/cssgen.php

## Summary
Severity: Medium
Advisory: GHSA-pr6q-g5gv-qgr7
CVE: CVE-2025-2123
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-03-09
Source: https://github.com/advisories/GHSA-pr6q-g5gv-qgr7
Type: github-advisory

## Affected
- Packagist: `geshi/geshi` — affected >=0

## Details
A vulnerability, which was classified as problematic, has been found in GeSHi up to 1.0.9.1. Affected by this issue is the function get_var of the file /contrib/cssgen.php of the component CSS Handler. The manipulation of the argument default-styles/keywords-1/keywords-2/keywords-3/keywords-4/comments leads to cross site scripting. The attack may be launched remotely. The exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2123
- https://github.com/GeSHi/geshi-1.0/issues/159
- https://github.com/GeSHi/geshi-1.0
- https://vuldb.com/?ctiid.299036
- https://vuldb.com/?id.299036
- https://vuldb.com/?submit.507418
