# [M] ALPINE-CVE-2017-16231

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-16231
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-16231
Type: osv

## Affected
- Alpine:v3.10: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.11: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.12: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.13: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.14: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.15: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.16: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.17: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.18: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.19: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.20: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.21: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.22: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.23: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.24: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.3: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.4: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.5: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.6: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.7: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.8: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.9: `pcre` — affected >=0 <7.8-r0
- Alpine:v3.10: `tiff` — affected >=0 <4.0.9-r0
- Alpine:v3.11: `tiff` — affected >=0 <4.0.9-r0
- Alpine:v3.12: `tiff` — affected >=0 <4.0.9-r0

## Details
In PCRE 8.41, after compiling, a pcretest load test PoC produces a crash overflow in the function match() in pcre_exec.c because of a self-recursive call. NOTE: third parties dispute the relevance of this report, noting that there are options that can be used to limit the amount of stack that is used

## References
- https://security.alpinelinux.org/vuln/CVE-2017-16231
