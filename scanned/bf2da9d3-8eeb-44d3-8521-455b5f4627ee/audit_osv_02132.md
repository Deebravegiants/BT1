# [M] ALPINE-CVE-2021-26933

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-26933
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-26933
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.9.0 <4.13.2-r5
- Alpine:v3.12: `xen` — affected >=4.9.0 <4.13.2-r5
- Alpine:v3.13: `xen` — affected >=4.9.0 <4.14.1-r2
- Alpine:v3.14: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.15: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.16: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.17: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.18: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.19: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.20: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.21: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.22: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.23: `xen` — affected >=4.9.0 <4.14.1-r3
- Alpine:v3.24: `xen` — affected >=4.9.0 <4.14.1-r3

## Details
An issue was discovered in Xen 4.9 through 4.14.x. On Arm, a guest is allowed to control whether memory accesses are bypassing the cache. This means that Xen needs to ensure that all writes (such as the ones during scrubbing) have reached the memory before handing over the page to a guest. Unfortunately, the operation to clean the cache is happening before checking if the page was scrubbed. Therefore there is no guarantee when all the writes will reach the memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-26933
