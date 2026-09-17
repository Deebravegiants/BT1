# [H] ALPINE-CVE-2021-44648

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-44648
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-44648
Type: osv

## Affected
- Alpine:v3.15: `gdk-pixbuf` — affected >=0 <2.42.8-r0
- Alpine:v3.16: `gdk-pixbuf` — affected >=0 <2.42.8-r0
- Alpine:v3.17: `gdk-pixbuf` — affected >=0 <2.42.8-r0
- Alpine:v3.18: `gdk-pixbuf` — affected >=0 <2.42.8-r0
- Alpine:v3.19: `gdk-pixbuf` — affected >=0 <2.42.8-r0
- Alpine:v3.20: `gdk-pixbuf` — affected >=0 <2.42.8-r0
- Alpine:v3.21: `gdk-pixbuf` — affected >=0 <2.42.8-r0
- Alpine:v3.22: `gdk-pixbuf` — affected >=0 <2.42.8-r0
- Alpine:v3.23: `gdk-pixbuf` — affected >=0 <2.42.8-r0

## Details
GNOME gdk-pixbuf 2.42.6 is vulnerable to a heap-buffer overflow vulnerability when decoding the lzw compressed stream of image data in GIF files with lzw minimum code size equals to 12.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-44648
