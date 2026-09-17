# [H] ALPINE-CVE-2026-12617

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-12617
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-12617
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.26-r0

## Details
The issue is unexpected program termination based on ordering and/or specific content in responses to queries for CNAME or DNAME, and A records. Specifically, if a client queries for a DNAME and A record below the DNAME to the resolver, and the authoritative server responds positively to the A query but delays the DNAME response and later responds negatively, `named` may quit unexpectedly. Or, if a client queries for a CNAME and A record for the same name to the resolver, and the authoritative server responds positively to the A query but delays the CNAME response and later responds with a self-referential CNAME, the same failure may occur.
This issue affects BIND 9 versions 9.18.0 through 9.18.50, 9.20.0 through 9.20.24, 9.18.11-S1 through 9.18.50-S1, and 9.20.9-S1 through 9.20.24-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-12617
