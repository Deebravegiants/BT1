# [M] ALPINE-CVE-2019-9494

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-9494
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-9494
Type: osv

## Affected
- Alpine:v3.10: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.11: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.12: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.13: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.14: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.15: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.16: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.17: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.18: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.19: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.20: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.21: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.22: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.23: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.24: `wpa_supplicant` — affected >=0 <2.7-r2
- Alpine:v3.9: `wpa_supplicant` — affected >=0 <2.7-r2

## Details
The implementations of SAE in hostapd and wpa_supplicant are vulnerable to side channel attacks as a result of observable timing differences and cache access patterns. An attacker may be able to gain leaked information from a side channel attack that can be used for full password recovery. Both hostapd with SAE support and wpa_supplicant with SAE support prior to and including version 2.7 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-9494
