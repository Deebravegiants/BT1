# [M] CVE-2017-15289

## Summary
Severity: Medium
Advisory: CVE-2017-15289
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-10-16
Source: https://osv.dev/vulnerability/CVE-2017-15289
Type: osv

## Details
The mode4and5 write functions in hw/display/cirrus_vga.c in Qemu allow local OS guest privileged users to cause a denial of service (out-of-bounds write access and Qemu process crash) via vectors related to dst calculation.

## References
- http://www.securityfocus.com/bid/101262
- https://access.redhat.com/errata/RHSA-2017:3368
- https://access.redhat.com/errata/RHSA-2017:3369
- https://access.redhat.com/errata/RHSA-2017:3466
- https://access.redhat.com/errata/RHSA-2017:3470
- https://access.redhat.com/errata/RHSA-2017:3471
- https://access.redhat.com/errata/RHSA-2017:3472
- https://access.redhat.com/errata/RHSA-2017:3473
- https://access.redhat.com/errata/RHSA-2017:3474
- https://access.redhat.com/errata/RHSA-2018:0516
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://usn.ubuntu.com/3575-1/
- https://www.debian.org/security/2018/dsa-4213
- https://bugzilla.redhat.com/show_bug.cgi?id=1501290
- http://www.openwall.com/lists/oss-security/2017/10/12/16
- https://lists.gnu.org/archive/html/qemu-devel/2017-10/msg02557.html
