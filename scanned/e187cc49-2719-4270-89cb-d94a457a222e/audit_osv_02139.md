# [H] ALPINE-CVE-2021-27803

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-27803
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-27803
Type: osv

## Affected
- Alpine:v3.10: `wpa_supplicant` — affected >=1.0 <2.8-r5
- Alpine:v3.11: `wpa_supplicant` — affected >=1.0 <2.9-r7
- Alpine:v3.12: `wpa_supplicant` — affected >=1.0 <2.9-r7
- Alpine:v3.13: `wpa_supplicant` — affected >=1.0 <2.9-r10
- Alpine:v3.14: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.15: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.16: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.17: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.18: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.19: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.20: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.21: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.22: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.23: `wpa_supplicant` — affected >=1.0 <2.9-r12
- Alpine:v3.24: `wpa_supplicant` — affected >=1.0 <2.9-r12

## Details
A vulnerability was discovered in how p2p/p2p_pd.c in wpa_supplicant before 2.10 processes P2P (Wi-Fi Direct) provision discovery requests. It could result in denial of service or other impact (potentially execution of arbitrary code), for an attacker within radio range.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-27803
