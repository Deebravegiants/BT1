# [M] ALPINE-CVE-2017-7650

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7650
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7650
Type: osv

## Affected
- Alpine:v3.10: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.11: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.12: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.13: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.14: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.15: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.16: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.17: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.18: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.19: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.20: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.21: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.22: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.23: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.24: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.3: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.4: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.5: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.6: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.7: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.8: `mosquitto` — affected >=0 <1.4.12-r0
- Alpine:v3.9: `mosquitto` — affected >=0 <1.4.12-r0

## Details
In Mosquitto before 1.4.12, pattern based ACLs can be bypassed by clients that set their username/client id to '#' or '+'. This allows locally or remotely connected clients to access MQTT topics that they do have the rights to. The same issue may be present in third party authentication/access control plugins for Mosquitto.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7650
