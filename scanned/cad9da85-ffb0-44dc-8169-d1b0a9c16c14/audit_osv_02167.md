# [M] ALPINE-CVE-2021-28700

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28700
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28700
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.12.0 <4.13.3-r2
- Alpine:v3.12: `xen` — affected >=4.12.0 <4.13.3-r2
- Alpine:v3.13: `xen` — affected >=4.12.0 <4.14.2-r0
- Alpine:v3.14: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.15: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.16: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.17: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.18: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.19: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.20: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.21: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.22: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.23: `xen` — affected >=4.12.0 <4.15.0-r2
- Alpine:v3.24: `xen` — affected >=4.12.0 <4.15.0-r2

## Details
xen/arm: No memory limit for dom0less domUs The dom0less feature allows an administrator to create multiple unprivileged domains directly from Xen. Unfortunately, the memory limit from them is not set. This allow a domain to allocate memory beyond what an administrator originally configured.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28700
