# [H] CVE-2026-3039

## Summary
Severity: High
Advisory: CVE-2026-3039
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-3039
Type: osv

## Details
BIND servers that are configured to use TKEY-based authentication via GSS-API tokens are vulnerable to excessive memory consumption when receiving and processing maliciously-constructed packets.  Typically these servers will be found in Active Directory integrated DNS deployments and/or Kerberos-secured DNS environments.
This issue affects BIND 9 versions 9.0.0 through 9.16.50, 9.18.0 through 9.18.48, 9.20.0 through 9.20.22, 9.21.0 through 9.21.21, 9.9.3-S1 through 9.16.50-S1, 9.18.11-S1 through 9.18.48-S1, and 9.20.9-S1 through 9.20.22-S1.

## References
- https://access.redhat.com/security/cve/CVE-2026-3039
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-3039.json
- https://access.redhat.com/errata/RHSA-2026:20334
- https://access.redhat.com/errata/RHSA-2026:23360
- https://access.redhat.com/errata/RHSA-2026:24338
- https://access.redhat.com/errata/RHSA-2026:24339
- https://access.redhat.com/errata/RHSA-2026:24367
- https://access.redhat.com/errata/RHSA-2026:24368
- https://access.redhat.com/errata/RHSA-2026:55441
- https://access.redhat.com/errata/RHSA-2026:57189
- https://access.redhat.com/errata/RHSA-2026:60383
- https://access.redhat.com/errata/RHSA-2026:62549
- https://kb.isc.org/docs/cve-2026-3039
- https://bugzilla.redhat.com/show_bug.cgi?id=2479767
- https://downloads.isc.org/isc/bind9/9.18.49
- https://downloads.isc.org/isc/bind9/9.20.23
- https://downloads.isc.org/isc/bind9/9.21.22
