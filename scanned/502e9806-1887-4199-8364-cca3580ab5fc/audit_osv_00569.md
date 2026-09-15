# [H] ALPINE-CVE-2017-16612

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-16612
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16612
Type: osv

## Affected
- Alpine:v3.10: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.11: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.12: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.13: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.14: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.15: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.16: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.17: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.18: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.19: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.20: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.21: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.22: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.23: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.24: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.4: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.5: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.6: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.7: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.8: `libxcursor` — affected >=0 <1.1.15-r0
- Alpine:v3.9: `libxcursor` — affected >=0 <1.1.15-r0

## Details
libXcursor before 1.1.15 has various integer overflows that could lead to heap buffer overflows when processing malicious cursors, e.g., with programs like GIMP. It is also possible that an attack vector exists against the related code in cursor/xcursor.c in Wayland through 1.14.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16612
