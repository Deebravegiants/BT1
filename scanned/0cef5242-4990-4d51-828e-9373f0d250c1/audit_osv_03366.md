# [H] ALPINE-CVE-2025-62291

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-62291
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-62291
Type: osv

## Affected
- Alpine:v3.20: `strongswan` — affected >=0 <5.9.13-r2
- Alpine:v3.21: `strongswan` — affected >=0 <5.9.14-r1
- Alpine:v3.22: `strongswan` — affected >=0 <5.9.14-r1
- Alpine:v3.23: `strongswan` — affected >=0 <5.9.14-r3
- Alpine:v3.24: `strongswan` — affected >=0 <5.9.14-r3

## Details
In the eap-mschapv2 plugin (client-side) in strongSwan before 6.0.3, a malicious EAP-MSCHAPv2 server can send a crafted message of size 6 through 8, and cause an integer underflow that potentially results in a heap-based buffer overflow.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-62291
