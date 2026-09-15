# [M] ALPINE-CVE-2018-14526

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-14526
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14526
Type: osv

## Affected
- Alpine:v3.10: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.11: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.12: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.13: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.14: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.15: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.16: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.17: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.18: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.19: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.20: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.21: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.22: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.23: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.24: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.5: `wpa_supplicant` — affected >=2.0 <2.6-r3
- Alpine:v3.6: `wpa_supplicant` — affected >=2.0 <2.6-r5
- Alpine:v3.7: `wpa_supplicant` — affected >=2.0 <2.6-r9
- Alpine:v3.8: `wpa_supplicant` — affected >=2.0 <2.6-r14
- Alpine:v3.9: `wpa_supplicant` — affected >=2.0 <2.6-r14

## Details
An issue was discovered in rsn_supp/wpa.c in wpa_supplicant 2.0 through 2.6. Under certain conditions, the integrity of EAPOL-Key messages is not checked, leading to a decryption oracle. An attacker within range of the Access Point and client can abuse the vulnerability to recover sensitive information.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14526
