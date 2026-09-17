# [H] ALPINE-CVE-2019-18197

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18197
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-10-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18197
Type: osv

## Affected
- Alpine:v3.10: `libxslt` — affected >=0 <1.1.33-r2
- Alpine:v3.11: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.12: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.13: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.14: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.15: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.16: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.17: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.18: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.19: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.20: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.21: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.22: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.23: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.24: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.7: `libxslt` — affected >=0 <1.1.31-r2
- Alpine:v3.8: `libxslt` — affected >=0 <1.1.33-r2
- Alpine:v3.9: `libxslt` — affected >=0 <1.1.33-r2

## Details
In xsltCopyText in transform.c in libxslt 1.1.33, a pointer variable isn't reset under certain circumstances. If the relevant memory area happened to be freed and reused in a certain way, a bounds check could fail and memory outside a buffer could be written to, or uninitialized data could be disclosed.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18197
