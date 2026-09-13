# [H] ALPINE-CVE-2016-6318

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6318
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6318
Type: osv

## Affected
- Alpine:v3.10: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.11: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.12: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.13: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.14: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.15: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.16: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.17: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.18: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.19: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.20: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.21: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.22: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.23: `cracklib` — affected >=2.9.0 <2.9.7-r0
- Alpine:v3.24: `cracklib` — affected >=2.9.0 <2.9.7-r0

## Details
Stack-based buffer overflow in the FascistGecosUser function in lib/fascist.c in cracklib allows local users to cause a denial of service (application crash) or gain privileges via a long GECOS field, involving longbuffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6318
