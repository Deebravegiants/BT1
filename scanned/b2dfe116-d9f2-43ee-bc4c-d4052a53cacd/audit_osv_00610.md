# [H] ALPINE-CVE-2017-2862

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-2862
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2862
Type: osv

## Affected
- Alpine:v3.3: `gdk-pixbuf` — affected >=0 <2.32.0-r2
- Alpine:v3.4: `gdk-pixbuf` — affected >=0 <2.34.0-r2
- Alpine:v3.5: `gdk-pixbuf` — affected >=0 <2.36.7-r0
- Alpine:v3.6: `gdk-pixbuf` — affected >=0 <2.36.7-r0

## Details
An exploitable heap overflow vulnerability exists in the gdk_pixbuf__jpeg_image_load_increment functionality of Gdk-Pixbuf 2.36.6. A specially crafted jpeg file can cause a heap overflow resulting in remote code execution. An attacker can send a file or url to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2862
