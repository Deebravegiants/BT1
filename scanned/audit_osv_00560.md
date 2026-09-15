# [M] ALPINE-CVE-2017-15874

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-15874
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15874
Type: osv

## Affected
- Alpine:v3.10: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.11: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.12: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.13: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.14: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.15: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.16: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.17: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.18: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.19: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.20: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.21: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.22: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.23: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.24: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.7: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.8: `busybox` — affected >=0 <1.27.2-r4
- Alpine:v3.9: `busybox` — affected >=0 <1.27.2-r4

## Details
archival/libarchive/decompress_unlzma.c in BusyBox 1.27.2 has an Integer Underflow that leads to a read access violation.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15874
