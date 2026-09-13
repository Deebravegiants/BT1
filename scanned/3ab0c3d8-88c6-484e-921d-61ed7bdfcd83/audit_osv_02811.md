# [H] ALPINE-CVE-2023-28366

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-28366
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-28366
Type: osv

## Affected
- Alpine:v3.18: `mosquitto` — affected >=1.3.2 <2.0.16-r0
- Alpine:v3.19: `mosquitto` — affected >=1.3.2 <2.0.16-r0
- Alpine:v3.20: `mosquitto` — affected >=1.3.2 <2.0.16-r0
- Alpine:v3.21: `mosquitto` — affected >=1.3.2 <2.0.16-r0
- Alpine:v3.22: `mosquitto` — affected >=1.3.2 <2.0.16-r0
- Alpine:v3.23: `mosquitto` — affected >=1.3.2 <2.0.16-r0
- Alpine:v3.24: `mosquitto` — affected >=1.3.2 <2.0.16-r0

## Details
The broker in Eclipse Mosquitto 1.3.2 through 2.x before 2.0.16 has a memory leak that can be abused remotely when a client sends many QoS 2 messages with duplicate message IDs, and fails to respond to PUBREC commands. This occurs because of mishandling of EAGAIN from the libc send function.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-28366
