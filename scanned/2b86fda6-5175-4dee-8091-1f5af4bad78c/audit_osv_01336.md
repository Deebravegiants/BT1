# [C] ALPINE-CVE-2019-11068

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2019-11068
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11068
Type: osv

## Affected
- Alpine:v3.10: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.11: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.12: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.13: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.14: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.15: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.16: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.17: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.18: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.19: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.20: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.21: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.22: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.23: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.24: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.6: `libxslt` — affected >=0 <1.1.29-r4
- Alpine:v3.7: `libxslt` — affected >=0 <1.1.31-r1
- Alpine:v3.8: `libxslt` — affected >=0 <1.1.33-r1
- Alpine:v3.9: `libxslt` — affected >=0 <1.1.33-r1

## Details
libxslt through 1.1.33 allows bypass of a protection mechanism because callers of xsltCheckRead and xsltCheckWrite permit access even upon receiving a -1 error code. xsltCheckRead can return -1 for a crafted URL that is not actually invalid and is subsequently loaded.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11068
