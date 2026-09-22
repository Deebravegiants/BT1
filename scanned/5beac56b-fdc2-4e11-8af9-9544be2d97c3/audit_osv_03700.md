# [H] ALPINE-CVE-2026-42488

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-42488
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42488
Type: osv

## Affected
- Alpine:v3.20: `xen` — affected >=0 <4.18.5-r9
- Alpine:v3.21: `xen` — affected >=0 <4.19.5-r4
- Alpine:v3.22: `xen` — affected >=0 <4.20.3-r4
- Alpine:v3.23: `xen` — affected >=0 <4.20.3-r4
- Alpine:v3.24: `xen` — affected >=0 <4.21.1-r6

## Details
Some shadow paging errors paths will switch the page-tables without
updating the currently running vCPU reference.  This causes a mismatch
between the loaded page-tables and the mapcache metadata which can lead
to corruption of the mapcache.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42488
