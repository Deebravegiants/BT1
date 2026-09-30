# [M] CVE-2016-4020

## Summary
Severity: Medium
Advisory: CVE-2016-4020
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2016-05-25
Source: https://osv.dev/vulnerability/CVE-2016-4020
Type: osv

## Details
The patch_instruction function in hw/i386/kvmvapic.c in QEMU does not initialize the imm32 variable, which allows local guest OS administrators to obtain sensitive information from host stack memory by accessing the Task Priority Register (TPR).

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=691a02e2ce0c413236a78dee6f2651c937b09fb0
- http://www.securityfocus.com/bid/86067
- http://www.ubuntu.com/usn/USN-2974-1
- https://access.redhat.com/errata/RHSA-2017:1856
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://bugzilla.redhat.com/show_bug.cgi?id=1313686
- https://lists.gnu.org/archive/html/qemu-devel/2016-04/msg01106.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-04/msg01118.html
