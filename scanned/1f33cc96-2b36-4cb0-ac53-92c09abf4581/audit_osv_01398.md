# [M] ALPINE-CVE-2019-13117

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-13117
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13117
Type: osv

## Affected
- Alpine:v3.10: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.11: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.12: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.13: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.14: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.15: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.16: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.17: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.18: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.19: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.20: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.21: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.22: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.23: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.24: `libxslt` — affected >=0 <1.1.34-r0
- Alpine:v3.8: `libxslt` — affected >=0 <1.1.33-r3
- Alpine:v3.9: `libxslt` — affected >=0 <1.1.33-r3

## Details
In numbers.c in libxslt 1.1.33, an xsl:number with certain format strings could lead to a uninitialized read in xsltNumberFormatInsertNumbers. This could allow an attacker to discern whether a byte on the stack contains the characters A, a, I, i, or 0, or any other character.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13117
