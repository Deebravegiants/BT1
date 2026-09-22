# [M] jq: Stack overflow via unbounded recursion in jv_contains

## Summary
Severity: Medium
Advisory: CVE-2026-40612
Aliases: GHSA-r7m6-x9c7-h69j
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-40612
Type: osv

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, jv_contains recurses into nested arrays/objects with no depth limit. With a sufficiently nested input structure (built programmatically with reduce, since the JSON parser caps at depth 10000), the C stack is exhausted.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40612.json
- https://github.com/jqlang/jq/security/advisories/GHSA-r7m6-x9c7-h69j
- https://nvd.nist.gov/vuln/detail/CVE-2026-40612
