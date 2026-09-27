# [H] @zag-js/core prototype pollution

## Summary
Severity: High
Advisory: GHSA-fg4m-w35q-vfg2
CVE: CVE-2024-57079
CWE: CWE-1321, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-fg4m-w35q-vfg2
Type: github-advisory

## Affected
- npm: `@zag-js/core` — affected >=0 <0.82.2

## Details
A prototype pollution in the lib.deepMerge function of @zag-js/core v0.50.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57079
- https://github.com/chakra-ui/zag/pull/2255
- https://github.com/chakra-ui/zag/commit/f53edc548f737aadfdd486a0043bdd5f5c068bbf
- https://gist.github.com/tariqhawis/4778fc57084766b7b7fb6d25d20b7b9b
- https://github.com/chakra-ui/zag
