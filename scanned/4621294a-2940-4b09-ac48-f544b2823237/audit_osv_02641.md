# [H] ALPINE-CVE-2022-40304

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-40304
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-40304
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
An issue was discovered in libxml2 before 2.10.3. Certain invalid XML entity definitions can corrupt a hash table key, potentially leading to subsequent logic errors. In one case, a double-free can be provoked.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-40304
