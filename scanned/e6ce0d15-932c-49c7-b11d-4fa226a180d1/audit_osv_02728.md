# [H] ALPINE-CVE-2022-45142

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-45142
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-45142
Type: osv

## Affected
- Alpine:v3.14: `heimdal` — affected >=0 <7.7.1-r1
- Alpine:v3.15: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.16: `heimdal` — affected >=0 <7.7.1-r0
- Alpine:v3.17: `heimdal` — affected >=0 <7.8.0-r1
- Alpine:v3.18: `heimdal` — affected >=0 <7.8.0-r2
- Alpine:v3.19: `heimdal` — affected >=0 <7.8.0-r2
- Alpine:v3.20: `heimdal` — affected >=0 <7.8.0-r2
- Alpine:v3.21: `heimdal` — affected >=0 <7.8.0-r2
- Alpine:v3.22: `heimdal` — affected >=0 <7.8.0-r2
- Alpine:v3.23: `heimdal` — affected >=0 <7.8.0-r2
- Alpine:v3.24: `heimdal` — affected >=0 <7.8.0-r2

## Details
The fix for CVE-2022-3437 included changing memcmp to be constant time and a workaround for a compiler bug by adding "!= 0" comparisons to the result of memcmp. When these patches were backported to the heimdal-7.7.1 and heimdal-7.8.0 branches (and possibly other branches) a logic inversion sneaked in causing the validation of message integrity codes in gssapi/arcfour to be inverted.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-45142
