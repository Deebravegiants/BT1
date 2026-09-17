# [H] ALPINE-CVE-2018-14404

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-14404
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14404
Type: osv

## Affected
- Alpine:v3.10: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.11: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.12: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.13: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.14: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.15: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.16: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.17: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.18: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.19: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.20: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.21: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.22: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.23: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.24: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.5: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.6: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.7: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.8: `libxml2` — affected >=0 <2.9.8-r1
- Alpine:v3.9: `libxml2` — affected >=0 <2.9.8-r1

## Details
A NULL pointer dereference vulnerability exists in the xpath.c:xmlXPathCompOpEval() function of libxml2 through 2.9.8 when parsing an invalid XPath expression in the XPATH_OP_AND or XPATH_OP_OR case. Applications processing untrusted XSL format inputs with the use of the libxml2 library may be vulnerable to a denial of service attack due to a crash of the application.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14404
