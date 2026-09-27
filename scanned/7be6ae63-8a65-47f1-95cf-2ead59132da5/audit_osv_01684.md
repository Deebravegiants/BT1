# [C] ALPINE-CVE-2019-9893

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-9893
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9893
Type: osv

## Affected
- Alpine:v3.10: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.11: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.12: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.13: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.14: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.15: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.16: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.17: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.18: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.19: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.20: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.21: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.22: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.23: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.24: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.8: `libseccomp` — affected >=0 <2.4.0-r0
- Alpine:v3.9: `libseccomp` — affected >=0 <2.4.0-r0

## Details
libseccomp before 2.4.0 did not correctly generate 64-bit syscall argument comparisons using the arithmetic operators (LT, GT, LE, GE), which might able to lead to bypassing seccomp filters and potential privilege escalations.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9893
