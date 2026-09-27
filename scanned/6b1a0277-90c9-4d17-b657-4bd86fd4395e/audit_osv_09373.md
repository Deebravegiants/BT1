# [C] CVE-2016-9603

## Summary
Severity: Critical
Advisory: CVE-2016-9603
CVSS: 9.9 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2016-9603
Type: osv

## Details
A heap buffer overflow flaw was found in QEMU's Cirrus CLGD 54xx VGA emulator's VNC display driver support before 2.9; the issue could occur when a VNC client attempted to update its display after a VGA operation is performed by a guest. A privileged user/process inside a guest could use this flaw to crash the QEMU process or, potentially, execute arbitrary code on the host with privileges of the QEMU process.

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- http://www.securityfocus.com/bid/96893
- http://www.securitytracker.com/id/1038023
- https://access.redhat.com/errata/RHSA-2017:0980
- https://access.redhat.com/errata/RHSA-2017:0981
- https://access.redhat.com/errata/RHSA-2017:0982
- https://access.redhat.com/errata/RHSA-2017:0983
- https://access.redhat.com/errata/RHSA-2017:0984
- https://access.redhat.com/errata/RHSA-2017:0985
- https://access.redhat.com/errata/RHSA-2017:0987
- https://access.redhat.com/errata/RHSA-2017:0988
- https://access.redhat.com/errata/RHSA-2017:1205
- https://access.redhat.com/errata/RHSA-2017:1206
- https://access.redhat.com/errata/RHSA-2017:1441
- https://lists.debian.org/debian-lts-announce/2018/02/msg00005.html
- https://security.gentoo.org/glsa/201706-03
- https://support.citrix.com/article/CTX221578
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9603
