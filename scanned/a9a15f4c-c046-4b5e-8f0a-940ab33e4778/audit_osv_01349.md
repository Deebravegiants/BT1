# [M] ALPINE-CVE-2019-11555

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-11555
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11555
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
- Alpine:v3.7: `hostapd` — affected >=0 <2.6-r4
- Alpine:v3.8: `hostapd` — affected >=0 <2.6-r5
- Alpine:v3.9: `hostapd` — affected >=0 <2.7-r1
- Alpine:v3.10: `wpa_supplicant` — affected >=0 <2.7-r3
- Alpine:v3.11: `wpa_supplicant` — affected >=0 <2.7-r3
- Alpine:v3.12: `wpa_supplicant` — affected >=0 <2.7-r3
- Alpine:v3.13: `wpa_supplicant` — affected >=0 <2.7-r3
- Alpine:v3.14: `wpa_supplicant` — affected >=0 <2.7-r3
- Alpine:v3.15: `wpa_supplicant` — affected >=0 <2.7-r3
- Alpine:v3.16: `wpa_supplicant` — affected >=0 <2.7-r3

## Details
The EAP-pwd implementation in hostapd (EAP server) before 2.8 and wpa_supplicant (EAP peer) before 2.8 does not validate fragmentation reassembly state properly for a case where an unexpected fragment could be received. This could result in process termination due to a NULL pointer dereference (denial of service). This affects eap_server/eap_server_pwd.c and eap_peer/eap_pwd.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11555
