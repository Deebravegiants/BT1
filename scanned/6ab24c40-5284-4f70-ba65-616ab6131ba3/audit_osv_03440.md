# [H] ALPINE-CVE-2026-13204

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-13204
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-13204
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.26-r0

## Details
If a provably insecure domain is covered by both an NSEC and NSEC3 record at the parent, and there exist an RRSIG for only one of these types, then BIND may exit unexpectedly with an assertion while validating this proof.
This issue affects BIND 9 versions 9.11.0 through 9.18.50, 9.20.0 through 9.20.24, 9.21.0 through 9.21.23, 9.11.3-S1 through 9.18.50-S1, and 9.20.9-S1 through 9.20.24-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-13204
