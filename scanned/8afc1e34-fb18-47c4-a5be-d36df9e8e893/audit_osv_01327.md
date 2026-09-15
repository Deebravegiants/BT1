# [H] ALPINE-CVE-2019-10208

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-10208
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-10208
Type: osv

## Affected
- Alpine:v3.10: `postgresql` — affected >=9.4.0 <11.5-r0
- Alpine:v3.11: `postgresql` — affected >=9.4.0 <11.5-r0
- Alpine:v3.12: `postgresql` — affected >=9.4.0 <11.5-r0
- Alpine:v3.13: `postgresql` — affected >=9.4.0 <11.5-r0
- Alpine:v3.14: `postgresql` — affected >=9.4.0 <11.5-r0
- Alpine:v3.7: `postgresql` — affected >=9.4.0 <10.10-r0
- Alpine:v3.8: `postgresql` — affected >=9.4.0 <10.10-r0
- Alpine:v3.9: `postgresql` — affected >=9.4.0 <11.5-r0
- Alpine:v3.15: `postgresql14` — affected >=0 <11.5-r0
- Alpine:v3.16: `postgresql14` — affected >=0 <11.5-r0
- Alpine:v3.17: `postgresql14` — affected >=0 <11.5-r0
- Alpine:v3.18: `postgresql14` — affected >=0 <11.5-r0
- Alpine:v3.17: `postgresql15` — affected >=0 <11.5-r0
- Alpine:v3.18: `postgresql15` — affected >=0 <11.5-r0
- Alpine:v3.19: `postgresql15` — affected >=0 <11.5-r0
- Alpine:v3.20: `postgresql15` — affected >=0 <11.5-r0

## Details
A flaw was discovered in postgresql versions 9.4.x before 9.4.24, 9.5.x before 9.5.19, 9.6.x before 9.6.15, 10.x before 10.10 and 11.x before 11.5 where arbitrary SQL statements can be executed given a suitable SECURITY DEFINER function. An attacker, with EXECUTE permission on the function, can execute arbitrary SQL as the owner of the function.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-10208
