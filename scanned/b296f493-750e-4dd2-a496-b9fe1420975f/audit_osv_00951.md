# [M] ALPINE-CVE-2018-12546

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-12546
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12546
Type: osv

## Affected
- Alpine:v3.10: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.11: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.12: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.13: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.14: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.15: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.16: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.17: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.18: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.19: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.20: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.21: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.22: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.23: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.24: `mosquitto` — affected >=1.0 <1.5.6-r0
- Alpine:v3.7: `mosquitto` — affected >=1.0 <1.4.15-r1
- Alpine:v3.8: `mosquitto` — affected >=1.0 <1.4.15-r5
- Alpine:v3.9: `mosquitto` — affected >=1.0 <1.5.6-r0

## Details
In Eclipse Mosquitto version 1.0 to 1.5.5 (inclusive) when a client publishes a retained message to a topic, then has its access to that topic revoked, the retained message will still be published to clients that subscribe to that topic in the future. In some applications this may result in clients being able cause effects that would otherwise not be allowed.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12546
