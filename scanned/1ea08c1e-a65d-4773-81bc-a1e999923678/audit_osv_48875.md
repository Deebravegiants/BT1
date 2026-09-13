# [M] CVE-2018-16838

## Summary
Severity: Medium
Advisory: CVE-2018-16838
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2018-16838
Type: osv

## Details
A flaw was found in sssd Group Policy Objects implementation. When the GPO is not readable by SSSD due to a too strict permission settings on the server side, SSSD will allow all authenticated users to login instead of denying access.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00051.html
- https://access.redhat.com/errata/RHSA-2019:3651
- https://access.redhat.com/errata/RHSA-2019:2177
- https://access.redhat.com/errata/RHSA-2019:2437
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16838
