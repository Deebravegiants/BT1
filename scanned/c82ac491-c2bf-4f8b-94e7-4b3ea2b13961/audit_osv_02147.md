# [M] ALPINE-CVE-2021-28166

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28166
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28166
Type: osv

## Affected
- Alpine:v3.14: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.15: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.16: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.17: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.18: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.19: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.20: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.21: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.22: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.23: `mosquitto` — affected >=2.0.0 <2.0.10-r0
- Alpine:v3.24: `mosquitto` — affected >=2.0.0 <2.0.10-r0

## Details
In Eclipse Mosquitto version 2.0.0 to 2.0.9, if an authenticated client that had connected with MQTT v5 sent a crafted CONNACK message to the broker, a NULL pointer dereference would occur.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28166
