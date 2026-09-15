# [M] ALPINE-CVE-2020-29385

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-29385
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-12-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29385
Type: osv

## Affected
- Alpine:v3.11: `gdk-pixbuf` — affected >=0 <2.40.0-r2
- Alpine:v3.12: `gdk-pixbuf` — affected >=0 <2.40.0-r4
- Alpine:v3.13: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.14: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.15: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.16: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.17: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.18: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.19: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.20: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.21: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.22: `gdk-pixbuf` — affected >=0 <2.42.2-r0
- Alpine:v3.23: `gdk-pixbuf` — affected >=0 <2.42.2-r0

## Details
GNOME gdk-pixbuf (aka GdkPixbuf) before 2.42.2 allows a denial of service (infinite loop) in lzw.c in the function write_indexes. if c->self_code equals 10, self->code_table[10].extends will assign the value 11 to c. The next execution in the loop will assign self->code_table[11].extends to c, which will give the value of 10. This will make the loop run infinitely. This bug can, for example, be triggered by calling this function with a GIF image with LZW compression that is crafted in a special way.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29385
