# [M] ALPINE-CVE-2021-28699

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28699
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28699
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=4.10.0 <4.13.3-r2
- Alpine:v3.12: `xen` — affected >=4.10.0 <4.13.3-r2
- Alpine:v3.13: `xen` — affected >=4.10.0 <4.14.2-r0
- Alpine:v3.14: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.15: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.16: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.17: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.18: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.19: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.20: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.21: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.22: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.23: `xen` — affected >=4.10.0 <4.15.0-r2
- Alpine:v3.24: `xen` — affected >=4.10.0 <4.15.0-r2

## Details
inadequate grant-v2 status frames array bounds check The v2 grant table interface separates grant attributes from grant status. That is, when operating in this mode, a guest has two tables. As a result, guests also need to be able to retrieve the addresses that the new status tracking table can be accessed through. For 32-bit guests on x86, translation of requests has to occur because the interface structure layouts commonly differ between 32- and 64-bit. The translation of the request to obtain the frame numbers of the grant status table involves translating the resulting array of frame numbers. Since the space used to carry out the translation is limited, the translation layer tells the core function the capacity of the array within translation space. Unfortunately the core function then only enforces array bounds to be below 8 times the specified value, and would write past the available space if enough frame numbers needed storing.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28699
