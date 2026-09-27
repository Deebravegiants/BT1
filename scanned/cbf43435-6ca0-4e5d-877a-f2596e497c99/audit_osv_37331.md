# [H] CVE-2026-3104

## Summary
Severity: High
Advisory: CVE-2026-3104
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-3104
Type: osv

## Details
A specially crafted domain can be used to cause a memory leak in a BIND resolver simply by querying this domain.
This issue affects BIND 9 versions 9.20.0 through 9.20.20, 9.21.0 through 9.21.19, and 9.20.9-S1 through 9.20.20-S1.
BIND 9 versions 9.18.0 through 9.18.46 and 9.18.11-S1 through 9.18.46-S1 are NOT affected.

## References
- https://access.redhat.com/security/cve/CVE-2026-3104
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-3104.json
- https://access.redhat.com/errata/RHSA-2026:6935
- https://kb.isc.org/docs/cve-2026-3104
- https://bugzilla.redhat.com/show_bug.cgi?id=2451310
- https://downloads.isc.org/isc/bind9/9.20.21
- https://downloads.isc.org/isc/bind9/9.21.20
