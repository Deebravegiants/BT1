# [H] ALPINE-CVE-2026-11605

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-11605
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11605
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.26-r0

## Details
The issue is a resource exhaustion vulnerability associated with DNSSEC validation. BIND always validates all RRSIG records in an answer, even if they are not strictly needed. A query to an authoritative server/zone which returns many valid but superfluous RRSIG records causes the validator to waste disproportionate CPU time.
This issue affects BIND 9 versions 9.20.0 through 9.20.24, 9.21.0 through 9.21.23, and 9.20.9-S1 through 9.20.24-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11605
