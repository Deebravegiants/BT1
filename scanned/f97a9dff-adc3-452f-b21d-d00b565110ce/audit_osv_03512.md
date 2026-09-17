# [M] ALPINE-CVE-2026-23557

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-23557
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-23557
Type: osv

## Affected
- Alpine:v3.20: `xen` — affected >=4.2.0 <4.18.5-r7
- Alpine:v3.21: `xen` — affected >=4.2.0 <4.19.5-r2
- Alpine:v3.22: `xen` — affected >=4.2.0 <4.20.3-r2
- Alpine:v3.23: `xen` — affected >=4.2.0 <4.20.3-r2
- Alpine:v3.24: `xen` — affected >=4.2.0 <4.21.1-r3

## Details
Any guest can cause xenstored to crash by issuing a XS_RESET_WATCHES
command within a transaction due to an assert() triggering.

In case xenstored was built with NDEBUG #defined nothing bad will
happen, as assert() is doing nothing in this case. Note that the
default is not to define NDEBUG for xenstored builds even in release
builds of Xen.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-23557
