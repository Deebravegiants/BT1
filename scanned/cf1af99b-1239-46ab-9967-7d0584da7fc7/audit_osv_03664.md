# [H] ALPINE-CVE-2026-40200

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-40200
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40200
Type: osv

## Affected
- Alpine:v3.19: `musl` — affected >=0 <1.2.4_git20230717-r6
- Alpine:v3.20: `musl` — affected >=0 <1.2.5-r3
- Alpine:v3.21: `musl` — affected >=0 <1.2.5-r11
- Alpine:v3.22: `musl` — affected >=0 <1.2.5-r12
- Alpine:v3.23: `musl` — affected >=0 <1.2.5-r23
- Alpine:v3.24: `musl` — affected >=0 <1.2.6-r2

## Details
An issue was discovered in musl libc 0.7.10 through 1.2.6. Stack-based memory corruption can occur during qsort of very large arrays, due to incorrectly implemented double-word primitives. The number of elements must exceed about seven million, i.e., the 32nd Leonardo number on 32-bit platforms (or the 64th Leonardo number on 64-bit platforms, which is not practical).

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40200
