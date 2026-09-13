# [H] ALPINE-CVE-2017-7651

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7651
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7651
Type: osv

## Affected
- Alpine:v3.10: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.11: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.12: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.13: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.14: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.15: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.16: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.17: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.18: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.19: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.20: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.21: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.22: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.23: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.24: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.5: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.6: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.7: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.8: `mosquitto` — affected >=0 <1.4.15-r0
- Alpine:v3.9: `mosquitto` — affected >=0 <1.4.15-r0

## Details
In Eclipse Mosquitto 1.4.14, a user can shutdown the Mosquitto server simply by filling the RAM memory with a lot of connections with large payload. This can be done without authentications if occur in connection phase of MQTT protocol.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7651
