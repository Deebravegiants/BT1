# [H] ALPINE-CVE-2021-0326

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-0326
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-0326
Type: osv

## Affected
- Alpine:v3.10: `wpa_supplicant` — affected >=0 <2.8-r4
- Alpine:v3.11: `wpa_supplicant` — affected >=0 <2.9-r6
- Alpine:v3.12: `wpa_supplicant` — affected >=0 <2.9-r6
- Alpine:v3.13: `wpa_supplicant` — affected >=0 <2.9-r9
- Alpine:v3.14: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.15: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.16: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.17: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.18: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.19: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.20: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.21: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.22: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.23: `wpa_supplicant` — affected >=0 <2.9-r10
- Alpine:v3.24: `wpa_supplicant` — affected >=0 <2.9-r10

## Details
In p2p_copy_client_info of p2p.c, there is a possible out of bounds write due to a missing bounds check. This could lead to remote code execution if the target device is performing a Wi-Fi Direct search, with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android-10 Android-11 Android-8.1 Android-9Android ID: A-172937525

## References
- https://security.alpinelinux.org/vuln/CVE-2021-0326
