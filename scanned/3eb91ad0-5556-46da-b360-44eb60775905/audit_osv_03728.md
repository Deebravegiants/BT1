# [M] ALPINE-CVE-2026-43896

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-43896
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-43896
Type: osv

## Affected
- Alpine:v3.22: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.23: `jq` — affected >=0 <1.8.2-r0
- Alpine:v3.24: `jq` — affected >=0 <1.8.2-r0

## Details
jq is a command-line JSON processor. In 1.8.1 and earlier, unbounded recursion in jv_object_merge_recursive() allows a crafted jq program to crash the process with a segfault. The function is reachable through the * operator when both operands are objects.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-43896
