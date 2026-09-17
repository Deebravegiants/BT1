# [C] ALPINE-CVE-2017-10965

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-10965
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-10965
Type: osv

## Affected
- Alpine:v3.10: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.11: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.12: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.13: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.14: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.15: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.16: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.17: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.3: `irssi` — affected >=0 <0.8.21.r2
- Alpine:v3.4: `irssi` — affected >=0 <0.8.21.r2
- Alpine:v3.5: `irssi` — affected >=0 <0.8.21.r2
- Alpine:v3.7: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.8: `irssi` — affected >=0 <1.0.4-r0
- Alpine:v3.9: `irssi` — affected >=0 <1.0.4-r0

## Details
An issue was discovered in Irssi before 1.0.4. When receiving messages with invalid time stamps, Irssi would try to dereference a NULL pointer.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-10965
