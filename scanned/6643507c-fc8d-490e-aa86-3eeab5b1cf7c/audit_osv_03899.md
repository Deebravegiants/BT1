# [M] ALPINE-CVE-2026-62434

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-62434
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-62434
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
A guest started with Populated on Demand enabled (PoD) can attempt to
reclaim pages which aren't regular guest RAM.  This can cause corruption
of memory management state in Xen.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-62434
