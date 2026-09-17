# [C] CVE-2018-12549

## Summary
Severity: Critical
Advisory: CVE-2018-12549
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-11
Source: https://osv.dev/vulnerability/CVE-2018-12549
Type: osv

## Details
In Eclipse OpenJ9 version 0.11.0, the OpenJ9 JIT compiler may incorrectly omit a null check on the receiver object of an Unsafe call when accelerating it.

## References
- https://access.redhat.com/errata/RHSA-2019:0469
- https://access.redhat.com/errata/RHSA-2019:0472
- https://access.redhat.com/errata/RHSA-2019:0640
- https://access.redhat.com/errata/RHSA-2019:1238
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=544019
