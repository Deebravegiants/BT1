# [M] CVE-2026-3592

## Summary
Severity: Medium
Advisory: CVE-2026-3592
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-3592
Type: osv

## Details
BIND resolvers are vulnerable to an amplified resource consumption/exhaustion attack.  If a victim resolver makes a query to a specially crafted zone, the resolver will consume disproportionate resources.
This issue affects BIND 9 versions 9.11.0 through 9.16.50, 9.18.0 through 9.18.48, 9.20.0 through 9.20.22, 9.21.0 through 9.21.21, 9.11.3-S1 through 9.16.50-S1, 9.18.11-S1 through 9.18.48-S1, and 9.20.9-S1 through 9.20.22-S1.

## References
- https://kb.isc.org/docs/cve-2026-3592
- https://downloads.isc.org/isc/bind9/9.18.49
- https://downloads.isc.org/isc/bind9/9.20.23
- https://downloads.isc.org/isc/bind9/9.21.22
