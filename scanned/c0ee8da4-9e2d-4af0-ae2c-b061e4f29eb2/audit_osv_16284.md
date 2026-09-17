# [H] CVE-2019-3894

## Summary
Severity: High
Advisory: CVE-2019-3894
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-03
Source: https://osv.dev/vulnerability/CVE-2019-3894
Type: osv

## Details
It was discovered that the ElytronManagedThread in Wildfly's Elytron subsystem in versions from 11 to 16 stores a SecurityIdentity to run the thread as. These threads do not necessarily terminate if the keep alive time has not expired. This could allow a shared thread to use the wrong security identity when executing.

## References
- https://access.redhat.com/errata/RHSA-2019:1106
- https://access.redhat.com/errata/RHSA-2019:1107
- https://access.redhat.com/errata/RHSA-2019:1108
- https://access.redhat.com/errata/RHSA-2019:1140
- https://security.netapp.com/advisory/ntap-20190517-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3894
