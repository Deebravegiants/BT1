# [C] ALPINE-CVE-2022-23304

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-23304
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-23304
Type: osv

## Affected
- Alpine:v3.12: `hostapd` — affected >=0 <2.9-r4
- Alpine:v3.13: `hostapd` — affected >=0 <2.9-r4
- Alpine:v3.14: `hostapd` — affected >=0 <2.9-r4
- Alpine:v3.15: `hostapd` — affected >=0 <2.10-r0
- Alpine:v3.16: `hostapd` — affected >=0 <2.10-r0
- Alpine:v3.17: `hostapd` — affected >=0 <2.10-r0
- Alpine:v3.18: `hostapd` — affected >=0 <2.10-r0
- Alpine:v3.19: `hostapd` — affected >=0 <2.10-r0
- Alpine:v3.20: `hostapd` — affected >=0 <2.10-r0
- Alpine:v3.21: `hostapd` — affected >=0 <2.10-r0
- Alpine:v3.22: `hostapd` — affected >=0 <2.10-r0
- Alpine:v3.23: `hostapd` — affected >=0 <2.10-r0
- Alpine:v3.24: `hostapd` — affected >=0 <2.10-r0

## Details
The implementations of EAP-pwd in hostapd before 2.10 and wpa_supplicant before 2.10 are vulnerable to side-channel attacks as a result of cache access patterns. NOTE: this issue exists because of an incomplete fix for CVE-2019-9495.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-23304
