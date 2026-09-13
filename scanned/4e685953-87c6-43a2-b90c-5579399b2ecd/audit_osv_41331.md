# [M] CVE-2026-5947

## Summary
Severity: Medium
Advisory: CVE-2026-5947
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-5947
Type: osv

## Details
Undefined behavior may result due to a race condition leading to a use-after-free violation.  If BIND receives an incoming DNS message signed with SIG(0), it begins work to validate that signature.  If, during that validation, the "recursive-clients" limit is reached (as would occur during a query flood), and that same DNS message is discarded per the limit, there is a brief window of time while the SIG(0) validation may attempt to read the now-discarded DNS message.
This issue affects BIND 9 versions 9.20.0 through 9.20.22, 9.21.0 through 9.21.21, and 9.20.9-S1 through 9.20.22-S1.
BIND 9 versions 9.18.28 through 9.18.49 and 9.18.28-S1 through 9.18.49-S1 are NOT affected.

## References
- https://access.redhat.com/security/cve/CVE-2026-5947
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-5947.json
- https://access.redhat.com/errata/RHSA-2026:7412
- https://kb.isc.org/docs/cve-2026-5947
- https://bugzilla.redhat.com/show_bug.cgi?id=2479772
- https://downloads.isc.org/isc/bind9/9.20.23
- https://downloads.isc.org/isc/bind9/9.21.22
