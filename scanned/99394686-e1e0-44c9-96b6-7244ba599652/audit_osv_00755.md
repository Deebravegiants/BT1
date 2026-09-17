# [H] ALPINE-CVE-2017-7652

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7652
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7652
Type: osv

## Affected
- Alpine:v3.10: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.11: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.12: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.13: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.14: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.15: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.16: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.17: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.18: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.19: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.20: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.21: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.22: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.23: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.24: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.5: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.6: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.7: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.8: `mosquitto` — affected >=1.0 <1.4.15-r0
- Alpine:v3.9: `mosquitto` — affected >=1.0 <1.4.15-r0

## Details
In Eclipse Mosquitto 1.4.14, if a Mosquitto instance is set running with a configuration file, then sending a HUP signal to server triggers the configuration to be reloaded from disk. If there are lots of clients connected so that there are no more file descriptors/sockets available (default limit typically 1024 file descriptors on Linux), then opening the configuration file will fail.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7652
