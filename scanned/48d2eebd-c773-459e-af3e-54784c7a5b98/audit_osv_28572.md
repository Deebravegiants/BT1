# [M] era-compiler-solidity contains a `xor(zext(cmp), -1)` misoptimization

## Summary
Severity: Medium
Advisory: CVE-2024-34704
Aliases: GHSA-22pj-7cvw-r3gc
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-34704
Type: osv

## Details
era-compiler-solidity is the ZKsync compiler for Solidity.  The problem occurred during instruction selection in the `DAGCombine` phase while visiting the XOR operation. The issue arises when attempting to fold the expression `!(x cc y)` into `(x !cc y)`. To perform this transformation, the second operand of XOR should be a constant representing the true value. However, it was incorrectly assumed that -1 represents the true value, when in fact, 1 is the correct representation, so this transformation for this case should be skipped. This vulnerability is fixed in 1.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34704.json
- https://github.com/matter-labs/era-compiler-solidity/security/advisories/GHSA-22pj-7cvw-r3gc
- https://nvd.nist.gov/vuln/detail/CVE-2024-34704
