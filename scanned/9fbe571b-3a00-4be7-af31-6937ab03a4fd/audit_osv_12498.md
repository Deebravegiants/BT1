# [C] CVE-2018-12547

## Summary
Severity: Critical
Advisory: CVE-2018-12547
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-11
Source: https://osv.dev/vulnerability/CVE-2018-12547
Type: osv

## Details
In Eclipse OpenJ9, prior to the 0.12.0 release, the jio_snprintf() and jio_vsnprintf() native methods ignored the length parameter. This affects existing APIs that called the functions to exceed the allocated buffer. This functions were not directly callable by non-native user code.

## References
- https://access.redhat.com/errata/RHSA-2019:0469
- https://access.redhat.com/errata/RHSA-2019:0472
- https://access.redhat.com/errata/RHSA-2019:0473
- https://access.redhat.com/errata/RHSA-2019:0474
- https://access.redhat.com/errata/RHSA-2019:0640
- https://access.redhat.com/errata/RHSA-2019:1238
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=543659
