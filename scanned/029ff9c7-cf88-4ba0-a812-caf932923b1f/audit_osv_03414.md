# [H] ALPINE-CVE-2026-11331

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-11331
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11331
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.26-r0

## Details
An attacker who knows (or guesses) that a resolver uses RPZ with wildcard CNAME policies can craft query names long enough to trigger a NAMETOOLONG error condition during RPZ processing. This is not handled correctly and may lead to defeating the RPZ rule. It also may lead to an unexpected exit of the BIND 9 software.
This issue affects BIND 9 versions 9.16.0 through 9.18.50, 9.20.0 through 9.20.24, 9.21.0 through 9.21.23, 9.16.8-S1 through 9.18.50-S1, and 9.20.9-S1 through 9.20.24-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11331
