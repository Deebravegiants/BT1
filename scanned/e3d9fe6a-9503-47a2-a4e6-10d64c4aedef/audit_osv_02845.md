# [H] ALPINE-CVE-2023-3592

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-3592
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-3592
Type: osv

## Affected
- Alpine:v3.18: `mosquitto` — affected >=0 <2.0.16-r0
- Alpine:v3.19: `mosquitto` — affected >=0 <2.0.16-r0
- Alpine:v3.20: `mosquitto` — affected >=0 <2.0.16-r0
- Alpine:v3.21: `mosquitto` — affected >=0 <2.0.16-r0
- Alpine:v3.22: `mosquitto` — affected >=0 <2.0.16-r0
- Alpine:v3.23: `mosquitto` — affected >=0 <2.0.16-r0
- Alpine:v3.24: `mosquitto` — affected >=0 <2.0.16-r0

## Details
In Mosquitto before 2.0.16, a memory leak occurs when clients send v5 CONNECT packets with a will message that contains invalid property types.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-3592
