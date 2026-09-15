# [H] ALPINE-CVE-2019-18218

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18218
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18218
Type: osv

## Affected
- Alpine:v3.10: `file` — affected >=0 <5.37-r1
- Alpine:v3.11: `file` — affected >=0 <5.37-r1
- Alpine:v3.12: `file` — affected >=0 <5.37-r1
- Alpine:v3.13: `file` — affected >=0 <5.37-r1
- Alpine:v3.14: `file` — affected >=0 <5.37-r1
- Alpine:v3.15: `file` — affected >=0 <5.37-r1
- Alpine:v3.16: `file` — affected >=0 <5.37-r1
- Alpine:v3.17: `file` — affected >=0 <5.37-r1
- Alpine:v3.18: `file` — affected >=0 <5.37-r1
- Alpine:v3.19: `file` — affected >=0 <5.37-r1
- Alpine:v3.20: `file` — affected >=0 <5.37-r1
- Alpine:v3.21: `file` — affected >=0 <5.37-r1
- Alpine:v3.22: `file` — affected >=0 <5.37-r1
- Alpine:v3.23: `file` — affected >=0 <5.37-r1
- Alpine:v3.24: `file` — affected >=0 <5.37-r1
- Alpine:v3.7: `file` — affected >=0 <5.32-r2
- Alpine:v3.8: `file` — affected >=0 <5.32-r2
- Alpine:v3.9: `file` — affected >=0 <5.36-r1

## Details
cdf_read_property_info in cdf.c in file through 5.37 does not restrict the number of CDF_VECTOR elements, which allows a heap-based buffer overflow (4-byte out-of-bounds write).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18218
