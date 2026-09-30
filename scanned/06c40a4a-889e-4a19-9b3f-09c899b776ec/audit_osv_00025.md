# [M] ALPINE-CVE-2015-9099

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2015-9099
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-9099
Type: osv

## Affected
- Alpine:v3.10: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.11: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.12: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.13: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.14: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.15: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.16: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.17: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.18: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.19: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.20: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.21: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.22: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.23: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.24: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.3: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.4: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.5: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.6: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.7: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.8: `lame` — affected >=0 <3.99.5-r6
- Alpine:v3.9: `lame` — affected >=0 <3.99.5-r6

## Details
The lame_init_params function in lame.c in libmp3lame.a in LAME 3.99.5 allows remote attackers to cause a denial of service (invalid read and application crash) via a crafted audio file with a negative sample rate.

## References
- https://security.alpinelinux.org/vuln/CVE-2015-9099
