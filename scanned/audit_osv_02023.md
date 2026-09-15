# [C] ALPINE-CVE-2020-8597

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-8597
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8597
Type: osv

## Affected
- Alpine:v3.10: `ppp` — affected >=0 <2.4.7-r7
- Alpine:v3.11: `ppp` — affected >=0 <2.4.7-r7
- Alpine:v3.12: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.13: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.14: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.15: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.16: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.17: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.18: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.19: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.20: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.21: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.22: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.23: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.24: `ppp` — affected >=0 <2.4.8-r1
- Alpine:v3.8: `ppp` — affected >=0 <2.4.7-r7
- Alpine:v3.9: `ppp` — affected >=0 <2.4.7-r7

## Details
eap.c in pppd in ppp 2.4.2 through 2.4.8 has an rhostname buffer overflow in the eap_request and eap_response functions.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8597
