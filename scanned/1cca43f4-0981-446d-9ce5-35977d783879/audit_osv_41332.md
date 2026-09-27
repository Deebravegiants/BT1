# [M] CVE-2026-5950

## Summary
Severity: Medium
Advisory: CVE-2026-5950
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-5950
Type: osv

## Details
An unbounded resend loop vulnerability exists in the BIND 9 resolver state machine during bad-server handling, enabling a remote unauthenticated attacker to cause severe resource exhaustion by sending queries that trigger specific retry conditions.
This issue affects BIND 9 versions 9.18.36 through 9.18.48, 9.20.8 through 9.20.22, 9.21.7 through 9.21.21, 9.18.36-S1 through 9.18.48-S1, and 9.20.9-S1 through 9.20.22-S1.

## References
- https://kb.isc.org/docs/cve-2026-5950
- https://downloads.isc.org/isc/bind9/9.18.49
- https://downloads.isc.org/isc/bind9/9.20.23
- https://downloads.isc.org/isc/bind9/9.21.22
