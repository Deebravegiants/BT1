# [H] ALPINE-CVE-2020-14148

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-14148
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14148
Type: osv

## Affected
- Alpine:v3.10: `ngircd` — affected >=0 <25-r1
- Alpine:v3.11: `ngircd` — affected >=0 <25-r1
- Alpine:v3.12: `ngircd` — affected >=0 <25-r1
- Alpine:v3.13: `ngircd` — affected >=0 <25-r1
- Alpine:v3.14: `ngircd` — affected >=0 <25-r1
- Alpine:v3.15: `ngircd` — affected >=0 <25-r1
- Alpine:v3.16: `ngircd` — affected >=0 <25-r1
- Alpine:v3.17: `ngircd` — affected >=0 <25-r1
- Alpine:v3.18: `ngircd` — affected >=0 <25-r1
- Alpine:v3.19: `ngircd` — affected >=0 <25-r1
- Alpine:v3.20: `ngircd` — affected >=0 <25-r1
- Alpine:v3.21: `ngircd` — affected >=0 <25-r1
- Alpine:v3.22: `ngircd` — affected >=0 <25-r1
- Alpine:v3.23: `ngircd` — affected >=0 <25-r1
- Alpine:v3.24: `ngircd` — affected >=0 <25-r1
- Alpine:v3.9: `ngircd` — affected >=0 <24-r5

## Details
The Server-Server protocol implementation in ngIRCd before 26~rc2 allows an out-of-bounds access, as demonstrated by the IRC_NJOIN() function.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14148
