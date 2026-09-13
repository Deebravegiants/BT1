# [H] javascript-deobfuscator crafted payload can lead to code execution

## Summary
Severity: High
Advisory: GHSA-9p6p-8v9r-8c9m
CVE: CVE-2024-36120
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-9p6p-8v9r-8c9m
Type: github-advisory

## Affected
- npm: `js-deobfuscator` — affected >=0 <1.1.0

## Details
javascript-deobfuscator removes common JavaScript obfuscation techniques. Crafted payloads targeting expression simplification can lead to code execution. This issue has been patched in version 1.1.0.

## References
- https://github.com/ben-sb/javascript-deobfuscator/security/advisories/GHSA-9p6p-8v9r-8c9m
- https://nvd.nist.gov/vuln/detail/CVE-2024-36120
- https://github.com/ben-sb/javascript-deobfuscator/commit/630d3caec83d5f31c5f7a07e6fadf613d06699d6
- https://github.com/ben-sb/javascript-deobfuscator
