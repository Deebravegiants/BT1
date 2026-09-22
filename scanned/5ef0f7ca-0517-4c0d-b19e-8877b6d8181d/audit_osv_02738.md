# [H] ALPINE-CVE-2022-48622

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-48622
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-48622
Type: osv

## Affected
- Alpine:v3.17: `gdk-pixbuf` — affected >=0 <2.42.12-r0
- Alpine:v3.18: `gdk-pixbuf` — affected >=0 <2.42.12-r0
- Alpine:v3.19: `gdk-pixbuf` — affected >=0 <2.42.12-r0
- Alpine:v3.20: `gdk-pixbuf` — affected >=0 <2.42.12-r0
- Alpine:v3.21: `gdk-pixbuf` — affected >=0 <2.42.12-r0
- Alpine:v3.22: `gdk-pixbuf` — affected >=0 <2.42.12-r0
- Alpine:v3.23: `gdk-pixbuf` — affected >=0 <2.42.12-r0

## Details
In GNOME GdkPixbuf (aka gdk-pixbuf) through 2.42.10, the ANI (Windows animated cursor) decoder encounters heap memory corruption (in ani_load_chunk in io-ani.c) when parsing chunks in a crafted .ani file. A crafted file could allow an attacker to overwrite heap metadata, leading to a denial of service or code execution attack. This occurs in gdk_pixbuf_set_option() in gdk-pixbuf.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-48622
