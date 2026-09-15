# [M] CVE-2019-3811

## Summary
Severity: Medium
Advisory: CVE-2019-3811
CVSS: 5.2 (CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2019-3811
Type: osv

## Details
A vulnerability was found in sssd. If a user was configured with no home directory set, sssd would return '/' (the root directory) instead of '' (the empty string / no home directory). This could impact services that restrict the user's filesystem access to within their home directory through chroot() etc. All versions before 2.1 are vulnerable.

## References
- http://www.securityfocus.com/bid/106644
- https://lists.debian.org/debian-lts-announce/2023/05/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00045.html
- https://access.redhat.com/errata/RHSA-2019:2177
- https://lists.debian.org/debian-lts-announce/2019/01/msg00011.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3811
