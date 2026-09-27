# [M] ALPINE-CVE-2026-10822

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-10822
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-10822
Type: osv

## Affected
- Alpine:v3.22: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.23: `bind` — affected >=0 <9.20.26-r0
- Alpine:v3.24: `bind` — affected >=0 <9.20.26-r0

## Details
If BIND encounters a particular invalid data structure in a DNS record, it will accept the invalid data, and may subsequently abort and exit.

BIND will first need to store a DNS record for a key (KEY, DNSKEY, etc.). That key must specify a PRIVATEDNS algorithm (253), and in the algorithm identifier, improperly give a length longer than the actual identifier data. The invalid identifier will be stored. If BIND later needs to render that record to text, it will use the invalid length during processing, leading to a consistency check failing.
This issue affects BIND 9 versions 9.18.0 through 9.18.50, 9.20.0 through 9.20.24, 9.21.0 through 9.21.23, 9.18.11-S1 through 9.18.50-S1, and 9.20.9-S1 through 9.20.24-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-10822
