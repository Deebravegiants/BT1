# [M] ALPINE-CVE-2022-29824

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-29824
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-05-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-29824
Type: osv

## Affected
- Alpine:v3.12: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.13: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.14: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.15: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.16: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.17: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.18: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.19: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.20: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.21: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.9.14-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.9.14-r0

## Details
In libxml2 before 2.9.14, several buffer handling functions in buf.c (xmlBuf*) and tree.c (xmlBuffer*) don't check for integer overflows. This can result in out-of-bounds memory writes. Exploitation requires a victim to open a crafted, multi-gigabyte XML file. Other software using libxml2's buffer functions, for example libxslt through 1.1.35, is affected as well.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-29824
