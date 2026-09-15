# [M] node-re2: Out-of-bounds heap read in `replace`/`split` via a `Buffer` ending in a truncated multi-byte UTF-8 character → adjacent heap memory disclosed to JavaScript

## Summary
Severity: Medium
Advisory: CVE-2026-71498
Aliases: GHSA-j4r3-hg7j-8chg
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-71498
Type: osv

## Details
node-re2 provides RE2 regular expression bindings for Node.js. Prior to version 1.26.1, passing a Buffer whose final bytes form a truncated (incomplete) multi-byte UTF-8 sequence could cause the native binding to read past the end of the allocated buffer while attempting to decode the final, incomplete code point. This could result in an out-of-bounds read and potential disclosure of adjacent memory contents. This issue is fixed in version 1.26.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71498.json
- https://github.com/uhop/node-re2/security/advisories/GHSA-j4r3-hg7j-8chg
- https://nvd.nist.gov/vuln/detail/CVE-2026-71498
- https://github.com/uhop/node-re2/issues/272
- https://github.com/uhop/node-re2/commit/9d72042a6a0da5bc523908b04808ea0e23867cc4
