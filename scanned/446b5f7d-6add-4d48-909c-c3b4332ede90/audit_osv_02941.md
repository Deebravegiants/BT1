# [M] ALPINE-CVE-2023-52160

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-52160
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-52160
Type: osv

## Affected
- Alpine:v3.19: `wpa_supplicant` — affected >=0 <2.10-r10
- Alpine:v3.20: `wpa_supplicant` — affected >=0 <2.10-r11
- Alpine:v3.21: `wpa_supplicant` — affected >=0 <2.10-r11
- Alpine:v3.22: `wpa_supplicant` — affected >=0 <2.10-r11
- Alpine:v3.23: `wpa_supplicant` — affected >=0 <2.10-r11
- Alpine:v3.24: `wpa_supplicant` — affected >=0 <2.10-r11

## Details
The implementation of PEAP in wpa_supplicant through 2.10 allows authentication bypass. For a successful attack, wpa_supplicant must be configured to not verify the network's TLS certificate during Phase 1 authentication, and an eap_peap_decrypt vulnerability can then be abused to skip Phase 2 authentication. The attack vector is sending an EAP-TLV Success packet instead of starting Phase 2. This allows an adversary to impersonate Enterprise Wi-Fi networks.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-52160
