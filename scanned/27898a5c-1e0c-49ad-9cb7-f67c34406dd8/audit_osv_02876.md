# [M] ALPINE-CVE-2023-42364

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-42364
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-11-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-42364
Type: osv

## Affected
- Alpine:v3.17: `busybox` — affected >=0 <1.35.0-r31
- Alpine:v3.18: `busybox` — affected >=0 <1.36.1-r7
- Alpine:v3.19: `busybox` — affected >=0 <1.36.1-r19
- Alpine:v3.20: `busybox` — affected >=0 <1.36.1-r29
- Alpine:v3.21: `busybox` — affected >=0 <1.36.1-r30
- Alpine:v3.22: `busybox` — affected >=0 <1.36.1-r30
- Alpine:v3.23: `busybox` — affected >=0 <1.36.1-r30
- Alpine:v3.24: `busybox` — affected >=0 <1.36.1-r30

## Details
A use-after-free vulnerability in BusyBox v.1.36.1 allows attackers to cause a denial of service via a crafted awk pattern in the awk.c evaluate function.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-42364
