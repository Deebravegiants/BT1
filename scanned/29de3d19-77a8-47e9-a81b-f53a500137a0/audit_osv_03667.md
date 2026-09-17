# [M] ALPINE-CVE-2026-40612

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-40612
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40612
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, jv_contains recurses into nested arrays/objects with no depth limit. With a sufficiently nested input structure (built programmatically with reduce, since the JSON parser caps at depth 10000), the C stack is exhausted.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40612
