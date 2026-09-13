# [H] ALPINE-CVE-2019-15903

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-15903
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-15903
Type: osv

## Affected
- Alpine:v3.10: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.11: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.12: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.13: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.14: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.15: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.16: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.17: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.18: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.19: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.20: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.21: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.22: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.23: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.24: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.7: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.8: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.9: `expat` — affected >=0 <2.2.7-r1
- Alpine:v3.10: `python2` — affected >=0 <2.7.17-r0
- Alpine:v3.11: `python2` — affected >=0 <2.7.17-r0
- Alpine:v3.12: `python2` — affected >=0 <2.7.17-r0
- Alpine:v3.9: `python2` — affected >=0 <2.7.17-r0

## Details
In libexpat before 2.2.8, crafted XML input could fool the parser into changing from DTD parsing to document parsing too early; a consecutive call to XML_GetCurrentLineNumber (or XML_GetCurrentColumnNumber) then resulted in a heap-based buffer over-read.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-15903
