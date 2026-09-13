# [H] ALPINE-CVE-2025-49812

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-49812
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-49812
Type: osv

## Affected
- Alpine:v3.19: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.20: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.21: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.22: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.23: `apache2` — affected >=0 <2.4.64-r0
- Alpine:v3.24: `apache2` — affected >=0 <2.4.64-r0

## Details
In some mod_ssl configurations on Apache HTTP Server versions through to 2.4.63, an HTTP desynchronisation attack allows a man-in-the-middle attacker to hijack an HTTP session via a TLS upgrade.

Only configurations using "SSLEngine optional" to enable TLS upgrades are affected. Users are recommended to upgrade to version 2.4.64, which removes support for TLS upgrade.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-49812
