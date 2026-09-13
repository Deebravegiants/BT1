# [M] ALPINE-CVE-2020-28928

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-28928
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-28928
Type: osv

## Affected
- Alpine:v3.10: `musl` — affected >=0 <1.1.22-r4
- Alpine:v3.11: `musl` — affected >=0 <1.1.24-r3
- Alpine:v3.12: `musl` — affected >=0 <1.1.24-r10
- Alpine:v3.13: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.14: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.15: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.16: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.17: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.18: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.19: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.20: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.21: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.22: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.23: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.24: `musl` — affected >=0 <1.2.2_pre2-r0
- Alpine:v3.9: `musl` — affected >=0 <1.1.20-r6

## Details
In musl libc through 1.2.1, wcsnrtombs mishandles particular combinations of destination buffer size and source character limit, as demonstrated by an invalid write access (buffer overflow).

## References
- https://security.alpinelinux.org/vuln/CVE-2020-28928
