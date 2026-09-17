# [H] ALPINE-CVE-2026-12244

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-12244
Ecosystem: Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-12244
Type: osv

## Affected
- Alpine:v3.24: `nsd` — affected >=4.14.0 <4.14.3-r0

## Details
If NSD is configured as secondary for a zone, the primary of that zone can crash NSD with an AXFR containing a DNS message with a special crafted SVCB RR with an rdata size of 65512, that let's an (uint16_t) variable that is used to allocate space needed for the RR wrap (because total size > 65535), causing a heap overflow. The attacker can perform a controlled (RCE class) head write of up to 65509 bytes

## References
- https://security.alpinelinux.org/vuln/CVE-2026-12244
