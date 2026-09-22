# [M] ALPINE-CVE-2017-13088

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-13088
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.0/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-10-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-13088
Type: osv

## Affected
- Alpine:v3.10: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.11: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.12: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.13: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.14: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.15: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.16: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.17: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.18: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.19: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.20: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.21: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.22: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.23: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.24: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.5: `hostapd` — affected >=0 <2.6-r1
- Alpine:v3.6: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.7: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.8: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.9: `hostapd` — affected >=0 <2.6-r2
- Alpine:v3.10: `wpa_supplicant` — affected >=0 <2.6-r7
- Alpine:v3.11: `wpa_supplicant` — affected >=0 <2.6-r7
- Alpine:v3.12: `wpa_supplicant` — affected >=0 <2.6-r7
- Alpine:v3.13: `wpa_supplicant` — affected >=0 <2.6-r7
- Alpine:v3.14: `wpa_supplicant` — affected >=0 <2.6-r7

## Details
Wi-Fi Protected Access (WPA and WPA2) that support 802.11v allows reinstallation of the Integrity Group Temporal Key (IGTK) when processing a Wireless Network Management (WNM) Sleep Mode Response frame, allowing an attacker within radio range to replay frames from access points to clients.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-13088
