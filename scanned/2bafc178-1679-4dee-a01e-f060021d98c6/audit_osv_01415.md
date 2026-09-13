# [M] ALPINE-CVE-2019-13377

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-13377
Ecosystem: Alpine:v3.10, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13377
Type: osv

## Affected
- Alpine:v3.10: `hostapd` — affected >=2.0 <2.8-r1
- Alpine:v3.9: `hostapd` — affected >=2.0 <2.7-r4
- Alpine:v3.10: `wpa_supplicant` — affected >=0 <2.8-r2
- Alpine:v3.9: `wpa_supplicant` — affected >=0 <2.7-r4

## Details
The implementations of SAE and EAP-pwd in hostapd and wpa_supplicant 2.x through 2.8 are vulnerable to side-channel attacks as a result of observable timing differences and cache access patterns when Brainpool curves are used. An attacker may be able to gain leaked information from a side-channel attack that can be used for full password recovery.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13377
