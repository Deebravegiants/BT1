# [M] ALPINE-CVE-2017-6312

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-6312
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-6312
Type: osv

## Affected
- Alpine:v3.10: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.11: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.12: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.13: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.14: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.15: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.16: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.17: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.18: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.19: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.20: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.21: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.22: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.23: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.5: `gdk-pixbuf` — affected >=0 <2.36.6-r0
- Alpine:v3.6: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.7: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.8: `gdk-pixbuf` — affected >=0 <2.36.6-r1
- Alpine:v3.9: `gdk-pixbuf` — affected >=0 <2.36.6-r1

## Details
Integer overflow in io-ico.c in gdk-pixbuf allows context-dependent attackers to cause a denial of service (segmentation fault and application crash) via a crafted image entry offset in an ICO file, which triggers an out-of-bounds read, related to compiler optimizations.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-6312
