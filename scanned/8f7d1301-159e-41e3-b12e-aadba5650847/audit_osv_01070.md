# [C] ALPINE-CVE-2018-18751

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-18751
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-18751
Type: osv

## Affected
- Alpine:v3.11: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.12: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.13: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.14: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.15: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.16: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.17: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.18: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.19: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.20: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.21: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.22: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.23: `gettext` — affected >=0 <0.20.1-r0
- Alpine:v3.24: `gettext` — affected >=0 <0.20.1-r0

## Details
An issue was discovered in GNU gettext 0.19.8. There is a double free in default_add_message in read-catalog.c, related to an invalid free in po_gram_parse in po-gram-gen.y, as demonstrated by lt-msgfmt.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-18751
