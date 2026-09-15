# [H] ALPINE-CVE-2019-9496

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-9496
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9496
Type: osv

## Affected
- Alpine:v3.10: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.11: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.12: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.13: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.14: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.15: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.16: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.17: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.18: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.19: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.20: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.21: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.22: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.23: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.24: `hostapd` — affected >=0 <2.8-r0
- Alpine:v3.6: `hostapd` — affected >=0 <2.6-r3
- Alpine:v3.7: `hostapd` — affected >=0 <2.6-r5
- Alpine:v3.8: `hostapd` — affected >=0 <2.6-r6
- Alpine:v3.9: `hostapd` — affected >=0 <2.7-r3

## Details
An invalid authentication sequence could result in the hostapd process terminating due to missing state validation steps when processing the SAE confirm message when in hostapd/AP mode. All version of hostapd with SAE support are vulnerable. An attacker may force the hostapd process to terminate, performing a denial of service attack. Both hostapd with SAE support and wpa_supplicant with SAE support prior to and including version 2.7 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9496
