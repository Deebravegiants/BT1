# [H] ALPINE-CVE-2021-28701

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28701
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-09-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28701
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.0.0 <4.13.3-r3
- Alpine:v3.12: `xen` — affected >=4.0.0 <4.13.3-r3
- Alpine:v3.13: `xen` — affected >=4.0.0 <4.14.2-r1
- Alpine:v3.14: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.15: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.16: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.17: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.18: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.19: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.20: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.21: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.22: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.23: `xen` — affected >=4.0.0 <4.15.0-r3
- Alpine:v3.24: `xen` — affected >=4.0.0 <4.15.0-r3

## Details
Another race in XENMAPSPACE_grant_table handling Guests are permitted access to certain Xen-owned pages of memory. The majority of such pages remain allocated / associated with a guest for its entire lifetime. Grant table v2 status pages, however, are de-allocated when a guest switches (back) from v2 to v1. Freeing such pages requires that the hypervisor enforce that no parallel request can result in the addition of a mapping of such a page to a guest. That enforcement was missing, allowing guests to retain access to pages that were freed and perhaps re-used for other purposes. Unfortunately, when XSA-379 was being prepared, this similar issue was not noticed.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28701
