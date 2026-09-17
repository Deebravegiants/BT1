# [C] ALPINE-CVE-2022-1587

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-1587
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-05-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1587
Type: osv

## Affected
- Alpine:v3.13: `pcre2` — affected >=0 <10.36-r1
- Alpine:v3.14: `pcre2` — affected >=0 <10.36-r1
- Alpine:v3.15: `pcre2` — affected >=0 <10.40-r0
- Alpine:v3.16: `pcre2` — affected >=0 <10.40-r0
- Alpine:v3.17: `pcre2` — affected >=0 <10.40-r0
- Alpine:v3.18: `pcre2` — affected >=0 <10.40-r0
- Alpine:v3.19: `pcre2` — affected >=0 <10.40-r0
- Alpine:v3.20: `pcre2` — affected >=0 <10.40-r0
- Alpine:v3.21: `pcre2` — affected >=0 <10.40-r0
- Alpine:v3.22: `pcre2` — affected >=0 <10.40-r0
- Alpine:v3.23: `pcre2` — affected >=0 <10.40-r0
- Alpine:v3.24: `pcre2` — affected >=0 <10.40-r0

## Details
An out-of-bounds read vulnerability was discovered in the PCRE2 library in the get_recurse_data_length() function of the pcre2_jit_compile.c file. This issue affects recursions in JIT-compiled regular expressions caused by duplicate data transfers.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1587
