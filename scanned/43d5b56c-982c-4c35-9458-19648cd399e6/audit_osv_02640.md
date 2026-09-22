# [H] ALPINE-CVE-2022-40303

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-40303
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-40303
Type: osv

## Affected
- Alpine:v3.13: `libxml2` — affected >=0 <2.9.14-r2
- Alpine:v3.14: `libxml2` — affected >=0 <2.9.14-r2
- Alpine:v3.15: `libxml2` — affected >=0 <2.9.14-r2
- Alpine:v3.16: `libxml2` — affected >=0 <2.9.14-r2
- Alpine:v3.17: `libxml2` — affected >=0 <2.10.3-r0
- Alpine:v3.18: `libxml2` — affected >=0 <2.10.3-r0
- Alpine:v3.19: `libxml2` — affected >=0 <2.10.3-r0
- Alpine:v3.20: `libxml2` — affected >=0 <2.10.3-r0
- Alpine:v3.21: `libxml2` — affected >=0 <2.10.3-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.10.3-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.10.3-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.10.3-r0

## Details
An issue was discovered in libxml2 before 2.10.3. When parsing a multi-gigabyte XML document with the XML_PARSE_HUGE parser option enabled, several integer counters can overflow. This results in an attempt to access an array at a negative 2GB offset, typically leading to a segmentation fault.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-40303
