# [M] ALPINE-CVE-2019-6473

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-6473
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6473
Type: osv

## Affected
- Alpine:v3.17: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.18: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.19: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.20: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.21: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.22: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.23: `kea` — affected >=1.4.0 <1.7.2-r0
- Alpine:v3.24: `kea` — affected >=1.4.0 <1.7.2-r0

## Details
An invalid hostname option can trigger an assertion failure in the Kea DHCPv4 server process (kea-dhcp4), causing the server process to exit. Versions affected: 1.4.0 to 1.5.0, 1.6.0-beta1, and 1.6.0-beta2.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6473
