# [H] ALPINE-CVE-2024-31143

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-31143
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-31143
Type: osv

## Affected
- Alpine:v3.17: `xen` — affected >=4.4.0 <4.16.6-r1
- Alpine:v3.18: `xen` — affected >=4.4.0 <4.17.5-r0
- Alpine:v3.19: `xen` — affected >=4.4.0 <4.18.3-r0
- Alpine:v3.20: `xen` — affected >=4.4.0 <4.18.3-r0
- Alpine:v3.21: `xen` — affected >=4.4.0 <4.19.0-r0
- Alpine:v3.22: `xen` — affected >=4.4.0 <4.19.0-r0
- Alpine:v3.23: `xen` — affected >=4.4.0 <4.19.0-r0
- Alpine:v3.24: `xen` — affected >=4.4.0 <4.19.0-r0

## Details
An optional feature of PCI MSI called "Multiple Message" allows a
device to use multiple consecutive interrupt vectors.  Unlike for MSI-X,
the setting up of these consecutive vectors needs to happen all in one
go.  In this handling an error path could be taken in different
situations, with or without a particular lock held.  This error path
wrongly releases the lock even when it is not currently held.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-31143
