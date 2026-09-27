# [M] jq: stack overflow in deep structural equality

## Summary
Severity: Medium
Advisory: CVE-2026-47770
Aliases: GHSA-3pgx-frr7-3jxp
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-47770
Type: osv

## Details
jq is a command-line JSON processor. Prior to 1.8.2, comparing two sufficiently deeply nested arrays with the == operator exhausts the C stack on jq's ordinary command-line surface, resulting in denial of service via stack exhaustion (uncontrolled recursion). The crash occurs in jq's recursive structural comparison code, with the recursion repeating through jvp_array_equal() and jv_equal() in src/jv.c when comparing deeply nested arrays; a nearby sort comparator path through jv_cmp() in src/jv_aux.c overflows the stack at a larger nesting depth from  the same missing recursion guard. Anyone running jq comparisons on attacker-controlled deeply nested JSON values, or embedding jq in a context  where untrusted data can reach the == comparison path, is affected. This vulnerability is fixed in 1.8.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47770.json
- https://github.com/jqlang/jq/security/advisories/GHSA-3pgx-frr7-3jxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-47770
