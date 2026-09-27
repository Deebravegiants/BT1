# [H] ALPINE-CVE-2021-34432

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-34432
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-34432
Type: osv

## Affected
- Alpine:v3.11: `mosquitto` — affected >=0 <1.6.8-r1
- Alpine:v3.12: `mosquitto` — affected >=0 <1.6.9-r1
- Alpine:v3.13: `mosquitto` — affected >=0 <1.6.12-r3
- Alpine:v3.14: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.15: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.16: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.17: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.18: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.19: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.20: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.21: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.22: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.23: `mosquitto` — affected >=0 <2.0.8-r0
- Alpine:v3.24: `mosquitto` — affected >=0 <2.0.8-r0

## Details
In Eclipse Mosquitto versions 2.0.7 and earlier, the server will crash if the client tries to send a PUBLISH packet with topic length = 0.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-34432
