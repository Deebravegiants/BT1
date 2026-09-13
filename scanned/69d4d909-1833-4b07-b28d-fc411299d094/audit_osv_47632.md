# [H] CVE-2016-9637

## Summary
Severity: High
Advisory: CVE-2016-9637
CVSS: 7.5 (CVSS:3.0/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-9637
Type: osv

## Details
The (1) ioport_read and (2) ioport_write functions in Xen, when qemu is used as a device model within Xen, might allow local x86 HVM guest OS administrators to gain qemu process privileges via vectors involving an out-of-range ioport access.

## References
- https://lists.debian.org/debian-lts-announce/2018/02/msg00005.html
- https://support.citrix.com/article/CTX219136
- http://www.securityfocus.com/bid/94699
- http://www.securitytracker.com/id/1037397
- http://xenbits.xen.org/xsa/advisory-199.html
- https://security.gentoo.org/glsa/201612-56
- http://rhn.redhat.com/errata/RHSA-2016-2963.html
