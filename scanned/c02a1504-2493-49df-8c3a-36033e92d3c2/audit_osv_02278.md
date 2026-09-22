# [M] ALPINE-CVE-2021-38165

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-38165
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-38165
Type: osv

## Affected
- Alpine:v3.15: `lynx` — affected >=0 <2.8.9_p1-r3
- Alpine:v3.16: `lynx` — affected >=0 <2.8.9_p1-r3
- Alpine:v3.17: `lynx` — affected >=0 <2.8.9_p1-r3
- Alpine:v3.18: `lynx` — affected >=0 <2.8.9_p1-r3
- Alpine:v3.19: `lynx` — affected >=0 <2.8.9_p1-r3
- Alpine:v3.20: `lynx` — affected >=0 <2.8.9_p1-r3
- Alpine:v3.21: `lynx` — affected >=0 <2.8.9_p1-r3
- Alpine:v3.22: `lynx` — affected >=0 <2.8.9_p1-r3
- Alpine:v3.23: `lynx` — affected >=0 <2.8.9_p1-r3
- Alpine:v3.24: `lynx` — affected >=0 <2.8.9_p1-r3

## Details
Lynx through 2.8.9 mishandles the userinfo subcomponent of a URI, which allows remote attackers to discover cleartext credentials because they may appear in SNI data.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-38165
