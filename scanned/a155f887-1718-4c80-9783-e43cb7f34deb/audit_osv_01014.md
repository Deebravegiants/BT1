# [M] ALPINE-CVE-2018-15853

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-15853
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15853
Type: osv

## Affected
- Alpine:v3.18: `xkbcomp` — affected >=0 <1.5.0-r0
- Alpine:v3.19: `xkbcomp` — affected >=0 <1.5.0-r0
- Alpine:v3.20: `xkbcomp` — affected >=0 <1.5.0-r0
- Alpine:v3.21: `xkbcomp` — affected >=0 <1.5.0-r0
- Alpine:v3.22: `xkbcomp` — affected >=0 <1.5.0-r0
- Alpine:v3.23: `xkbcomp` — affected >=0 <1.5.0-r0
- Alpine:v3.24: `xkbcomp` — affected >=0 <1.5.0-r0

## Details
Endless recursion exists in xkbcomp/expr.c in xkbcommon and libxkbcommon before 0.8.1, which could be used by local attackers to crash xkbcommon users by supplying a crafted keymap file that triggers boolean negation.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15853
