# [H] ALPINE-CVE-2021-20270

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-20270
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-20270
Type: osv

## Affected
- Alpine:v3.14: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.15: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.16: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.17: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.18: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.19: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.20: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.21: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.22: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.23: `py3-pygments` — affected >=0 <2.7.4-r0
- Alpine:v3.24: `py3-pygments` — affected >=0 <2.7.4-r0

## Details
An infinite loop in SMLLexer in Pygments versions 1.5 to 2.7.3 may lead to denial of service when performing syntax highlighting of a Standard ML (SML) source file, as demonstrated by input that only contains the "exception" keyword.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-20270
