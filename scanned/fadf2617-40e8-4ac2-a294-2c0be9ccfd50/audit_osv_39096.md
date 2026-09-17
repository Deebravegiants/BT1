# [M] jq: Stack Overflow in Recursive Object Merge

## Summary
Severity: Medium
Advisory: CVE-2026-43896
Aliases: GHSA-mg96-6h3q-g846
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43896
Type: osv

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, unbounded recursion in jv_object_merge_recursive() allows a crafted jq program to crash the process with a segfault. The function is reachable through the * operator when both operands are objects.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43896.json
- https://github.com/jqlang/jq/security/advisories/GHSA-mg96-6h3q-g846
- https://nvd.nist.gov/vuln/detail/CVE-2026-43896
