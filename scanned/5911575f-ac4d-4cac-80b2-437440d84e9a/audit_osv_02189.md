# [M] ALPINE-CVE-2021-30004

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-30004
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-04-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-30004
Type: osv

## Affected
- Alpine:v3.11: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.12: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.13: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.14: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.15: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.16: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.17: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.18: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.19: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.20: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.21: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.22: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.23: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.24: `hostapd` — affected >=0 <2.9-r3
- Alpine:v3.11: `wpa_supplicant` — affected >=0 <2.9-r8
- Alpine:v3.12: `wpa_supplicant` — affected >=0 <2.9-r8
- Alpine:v3.13: `wpa_supplicant` — affected >=0 <2.9-r11
- Alpine:v3.14: `wpa_supplicant` — affected >=0 <2.9-r13
- Alpine:v3.15: `wpa_supplicant` — affected >=0 <2.9-r13
- Alpine:v3.16: `wpa_supplicant` — affected >=0 <2.9-r13
- Alpine:v3.17: `wpa_supplicant` — affected >=0 <2.9-r13
- Alpine:v3.18: `wpa_supplicant` — affected >=0 <2.9-r13
- Alpine:v3.19: `wpa_supplicant` — affected >=0 <2.9-r13
- Alpine:v3.20: `wpa_supplicant` — affected >=0 <2.9-r13
- Alpine:v3.21: `wpa_supplicant` — affected >=0 <2.9-r13

## Details
In wpa_supplicant and hostapd 2.9, forging attacks may occur because AlgorithmIdentifier parameters are mishandled in tls/pkcs1.c and tls/x509v3.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-30004
