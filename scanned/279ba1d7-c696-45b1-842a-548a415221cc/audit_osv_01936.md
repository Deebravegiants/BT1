# [M] ALPINE-CVE-2020-28368

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-28368
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-11-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-28368
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.4-r0
- Alpine:v3.11: `xen` — affected >=0 <4.13.2-r1
- Alpine:v3.12: `xen` — affected >=0 <4.13.2-r1
- Alpine:v3.13: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.14: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.15: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.16: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.17: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.18: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.19: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.20: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.21: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.22: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.23: `xen` — affected >=0 <4.14.0-r2
- Alpine:v3.24: `xen` — affected >=0 <4.14.0-r2

## Details
Xen through 4.14.x allows guest OS administrators to obtain sensitive information (such as AES keys from outside the guest) via a side-channel attack on a power/energy monitoring interface, aka a "Platypus" attack. NOTE: there is only one logically independent fix: to change the access control for each such interface in Xen.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-28368
