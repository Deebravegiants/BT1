# [H] ALPINE-CVE-2018-12543

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-12543
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12543
Type: osv

## Affected
- Alpine:v3.10: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.11: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.12: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.13: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.14: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.15: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.16: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.17: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.18: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.19: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.20: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.21: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.22: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.23: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.24: `mosquitto` — affected >=1.5.0 <1.5.3-r0
- Alpine:v3.9: `mosquitto` — affected >=1.5.0 <1.5.3-r0

## Details
In Eclipse Mosquitto versions 1.5 to 1.5.2 inclusive, if a message is published to Mosquitto that has a topic starting with $, but that is not $SYS, e.g. $test/test, then an assert is triggered that should otherwise not be reachable and Mosquitto will exit.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12543
