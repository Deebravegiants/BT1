# [H] ALPINE-CVE-2026-3238

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-3238
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3238
Type: osv

## Affected
- Alpine:v3.23: `samba` — affected >=0 <4.22.10-r0
- Alpine:v3.24: `samba` — affected >=0 <4.23.8-r0

## Details
A flaw was found in Samba’s WINS server component when running as an Active Directory Domain Controller. The WINS protocol handlers for certain request types did not properly validate incoming packets, allowing an unauthenticated remote attacker to trigger a NULL pointer dereference and crash the WINS service using specially crafted UDP packets.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3238
