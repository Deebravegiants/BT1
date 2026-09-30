# [H] ALPINE-CVE-2020-12762

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-12762
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-05-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-12762
Type: osv

## Affected
- Alpine:v3.10: `json-c` — affected >=0 <0.13.1-r1
- Alpine:v3.11: `json-c` — affected >=0 <0.13.1-r1
- Alpine:v3.12: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.13: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.14: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.15: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.16: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.17: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.18: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.19: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.20: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.21: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.22: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.23: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.24: `json-c` — affected >=0 <0.14-r1
- Alpine:v3.9: `json-c` — affected >=0 <0.13.1-r1
- Alpine:v3.15: `libfastjson` — affected >=0 <1.2304.0-r0
- Alpine:v3.16: `libfastjson` — affected >=0 <1.2304.0-r0
- Alpine:v3.17: `libfastjson` — affected >=0 <1.2304.0-r0
- Alpine:v3.18: `libfastjson` — affected >=0 <1.2304.0-r0
- Alpine:v3.19: `libfastjson` — affected >=0 <1.2304.0-r0
- Alpine:v3.20: `libfastjson` — affected >=0 <1.2304.0-r0
- Alpine:v3.21: `libfastjson` — affected >=0 <1.2304.0-r0
- Alpine:v3.22: `libfastjson` — affected >=0 <1.2304.0-r0
- Alpine:v3.23: `libfastjson` — affected >=0 <1.2304.0-r0

## Details
json-c through 0.14 has an integer overflow and out-of-bounds write via a large JSON file, as demonstrated by printbuf_memappend.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-12762
