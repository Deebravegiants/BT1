# [C] ALPINE-CVE-2019-1010238

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-1010238
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1010238
Type: osv

## Affected
- Alpine:v3.10: `pango` — affected >=1.42.0 <1.42.4-r2
- Alpine:v3.11: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.12: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.13: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.14: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.15: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.16: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.17: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.18: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.19: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.20: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.21: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.22: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.23: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.24: `pango` — affected >=1.42.0 <1.44.1-r0
- Alpine:v3.9: `pango` — affected >=1.42.0 <1.42.4-r1

## Details
Gnome Pango 1.42 and later is affected by: Buffer Overflow. The impact is: The heap based buffer overflow can be used to get code execution. The component is: function name: pango_log2vis_get_embedding_levels, assignment of nchars and the loop condition. The attack vector is: Bug can be used when application pass invalid utf-8 strings to functions like pango_itemize.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1010238
