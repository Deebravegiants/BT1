# [M] ALPINE-CVE-2019-16275

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-16275
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-16275
Type: osv

## Affected
- Alpine:v3.10: `hostapd` — affected >=0 <2.8-r2
- Alpine:v3.11: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.12: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.13: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.14: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.15: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.16: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.17: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.18: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.19: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.20: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.21: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.22: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.23: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.24: `hostapd` — affected >=0 <2.9-r1
- Alpine:v3.7: `hostapd` — affected >=0 <2.6-r6
- Alpine:v3.8: `hostapd` — affected >=0 <2.6-r7
- Alpine:v3.9: `hostapd` — affected >=0 <2.7-r5
- Alpine:v3.10: `wpa_supplicant` — affected >=0 <2.8-r3
- Alpine:v3.11: `wpa_supplicant` — affected >=0 <2.9-r5
- Alpine:v3.12: `wpa_supplicant` — affected >=0 <2.9-r5
- Alpine:v3.13: `wpa_supplicant` — affected >=0 <2.9-r5
- Alpine:v3.14: `wpa_supplicant` — affected >=0 <2.9-r5
- Alpine:v3.15: `wpa_supplicant` — affected >=0 <2.9-r5
- Alpine:v3.16: `wpa_supplicant` — affected >=0 <2.9-r5

## Details
hostapd before 2.10 and wpa_supplicant before 2.10 allow an incorrect indication of disconnection in certain situations because source address validation is mishandled. This is a denial of service that should have been prevented by PMF (aka management frame protection). The attacker must send a crafted 802.11 frame from a location that is within the 802.11 communications range.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-16275
