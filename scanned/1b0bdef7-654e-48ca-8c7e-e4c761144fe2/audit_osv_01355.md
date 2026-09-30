# [M] ALPINE-CVE-2019-11779

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-11779
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11779
Type: osv

## Affected
- Alpine:v3.10: `mosquitto` — affected >=1.5 <1.6.3-r1
- Alpine:v3.11: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.12: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.13: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.14: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.15: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.16: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.17: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.18: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.19: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.20: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.21: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.22: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.23: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.24: `mosquitto` — affected >=1.5 <1.6.7-r0
- Alpine:v3.9: `mosquitto` — affected >=1.5 <1.5.6-r1

## Details
In Eclipse Mosquitto 1.5.0 to 1.6.5 inclusive, if a malicious MQTT client sends a SUBSCRIBE packet containing a topic that consists of approximately 65400 or more '/' characters, i.e. the topic hierarchy separator, then a stack overflow will occur.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11779
