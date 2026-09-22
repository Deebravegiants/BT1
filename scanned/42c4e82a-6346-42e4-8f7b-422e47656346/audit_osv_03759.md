# [M] ALPINE-CVE-2026-47770

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-47770
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-47770
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. Prior to 1.8.2, comparing two sufficiently deeply nested arrays with the == operator exhausts the C stack on jq's ordinary command-line surface, resulting in denial of service via stack exhaustion (uncontrolled recursion). The crash occurs in jq's recursive structural comparison code, with the recursion repeating through jvp_array_equal() and jv_equal() in src/jv.c when comparing deeply nested arrays; a nearby sort comparator path through jv_cmp() in src/jv_aux.c overflows the stack at a larger nesting depth from  the same missing recursion guard. Anyone running jq comparisons on attacker-controlled deeply nested JSON values, or embedding jq in a context  where untrusted data can reach the == comparison path, is affected. This vulnerability is fixed in 1.8.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-47770
