# [M] ALPINE-CVE-2017-14318

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-14318
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14318
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.11: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.12: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.13: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.14: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.15: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.16: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.17: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.18: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.19: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.20: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.21: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.22: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.23: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.24: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.3: `xen` — affected >=0 <4.6.3-r9
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r11
- Alpine:v3.5: `xen` — affected >=0 <4.7.2-r2
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r1
- Alpine:v3.7: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.8: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.9: `xen` — affected >=0 <4.9.0-r4

## Details
An issue was discovered in Xen 4.5.x through 4.9.x. The function `__gnttab_cache_flush` handles GNTTABOP_cache_flush grant table operations. It checks to see if the calling domain is the owner of the page that is to be operated on. If it is not, the owner's grant table is checked to see if a grant mapping to the calling domain exists for the page in question. However, the function does not check to see if the owning domain actually has a grant table or not. Some special domains, such as `DOMID_XEN`, `DOMID_IO` and `DOMID_COW` are created without grant tables. Hence, if __gnttab_cache_flush operates on a page owned by these special domains, it will attempt to dereference a NULL pointer in the domain struct.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14318
