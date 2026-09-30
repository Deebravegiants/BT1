# [H] ALPINE-CVE-2018-12550

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-12550
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12550
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
- Alpine:v3.8: `mosquitto` — affected >=1.0 <1.4.15-r4
- Alpine:v3.9: `mosquitto` — affected >=1.0 <1.5.6-r0

## Details
When Eclipse Mosquitto version 1.0 to 1.5.5 (inclusive) is configured to use an ACL file, and that ACL file is empty, or contains only comments or blank lines, then Mosquitto will treat this as though no ACL file has been defined and use a default allow policy. The new behaviour is to have an empty ACL file mean that all access is denied, which is not a useful configuration but is not unexpected.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12550
