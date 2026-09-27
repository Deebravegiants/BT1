# [H] ALPINE-CVE-2021-28831

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28831
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28831
Type: osv

## Affected
- Alpine:v3.10: `busybox` — affected >=1.32.0 <1.30.1-r5
- Alpine:v3.11: `busybox` — affected >=1.32.0 <1.31.1-r10
- Alpine:v3.12: `busybox` — affected >=1.32.0 <1.31.1-r20
- Alpine:v3.13: `busybox` — affected >=1.32.0 <1.32.1-r4
- Alpine:v3.14: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.15: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.16: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.17: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.18: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.19: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.20: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.21: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.22: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.23: `busybox` — affected >=1.32.0 <1.33.0-r5
- Alpine:v3.24: `busybox` — affected >=1.32.0 <1.33.0-r5

## Details
decompress_gunzip.c in BusyBox through 1.32.1 mishandles the error bit on the huft_build result pointer, with a resultant invalid free or segmentation fault, via malformed gzip data.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28831
