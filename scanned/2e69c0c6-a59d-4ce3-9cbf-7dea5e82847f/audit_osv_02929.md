# [M] ALPINE-CVE-2023-49582

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-49582
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-49582
Type: osv

## Affected
- Alpine:v3.17: `apr` — affected >=0 <1.7.5-r0
- Alpine:v3.18: `apr` — affected >=0 <1.7.5-r0
- Alpine:v3.19: `apr` — affected >=0 <1.7.5-r0
- Alpine:v3.20: `apr` — affected >=0 <1.7.5-r0
- Alpine:v3.21: `apr` — affected >=0 <1.7.5-r0
- Alpine:v3.22: `apr` — affected >=0 <1.7.5-r0
- Alpine:v3.23: `apr` — affected >=0 <1.7.5-r0
- Alpine:v3.24: `apr` — affected >=0 <1.7.5-r0

## Details
Lax permissions set by the Apache Portable Runtime library on Unix platforms would allow local users read access to named shared memory segments, potentially revealing sensitive application data. 

This issue does not affect non-Unix platforms, or builds with APR_USE_SHMEM_SHMGET=1 (apr.h)

Users are recommended to upgrade to APR version 1.7.5, which fixes this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-49582
