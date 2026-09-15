# [H] ALPINE-CVE-2026-12246

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-12246
Ecosystem: Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-12246
Type: osv

## Affected
- Alpine:v3.24: `nsd` — affected >=4.14.0 <4.14.3-r0

## Details
NSD version 4.14.0 introduced a bug where a specially crafted APL RR, with an adflength larger than permitted for the address family will overwrite the stack when the zone is written to disk, with a maximum of 111 attacker controlled bytes.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-12246
