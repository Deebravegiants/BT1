# [H] debug Inefficient Regular Expression Complexity vulnerability

## Summary
Severity: High
Advisory: GHSA-9vvw-cc9w-f27h
CVE: CVE-2017-20165
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-09
Source: https://github.com/advisories/GHSA-9vvw-cc9w-f27h
Type: github-advisory

## Affected
- npm: `debug` — affected >=3.0.0 <3.1.0
- npm: `debug` — affected >=0 <2.6.9

## Details
A vulnerability classified as problematic has been found in debug-js debug up to 3.0.x. This affects the function useColors of the file src/node.js. The manipulation of the argument str leads to inefficient regular expression complexity. Upgrading to version 3.1.0 is able to address this issue. The name of the patch is c38a0166c266a679c8de012d4eaccec3f944e685. It is recommended to upgrade the affected component. The identifier VDB-217665 was assigned to this vulnerability. The patch has been backported to the 2.6.x branch in version 2.6.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20165
- https://github.com/debug-js/debug/pull/504
- https://github.com/debug-js/debug/commit/c38a0166c266a679c8de012d4eaccec3f944e685
- https://github.com/debug-js/debug/commit/f53962e944a87e6ca9bb622a2a12dffc22a9bb5a
- https://github.com/debug-js/debug
- https://github.com/debug-js/debug/releases/tag/2.6.9
- https://github.com/debug-js/debug/releases/tag/3.1.0
- https://vuldb.com/?ctiid.217665
- https://vuldb.com/?id.217665
