# [H] ALPINE-CVE-2026-11721

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-11721
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11721
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.26-r0

## Details
It is possible for an attacker's zone to respond to a query with an RRSIG that has a smaller number of labels than the zone in which the RRSIG is contained. This causes `named` to produce a wildcard name for a zone that is shorter than the attacker's zone, which can result in cache poisoning. For this attack to have any effect, the resolver under attack must have set `synth-from-dnssec yes;` (which is the default).
This issue affects BIND 9 versions 9.11.0 through 9.18.50, 9.20.0 through 9.20.24, 9.21.0 through 9.21.23, 9.11.3-S1 through 9.18.50-S1, and 9.20.9-S1 through 9.20.24-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11721
