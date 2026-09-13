# [M] CVE-2017-9310

## Summary
Severity: Medium
Advisory: CVE-2017-9310
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-06-08
Source: https://osv.dev/vulnerability/CVE-2017-9310
Type: osv

## Details
QEMU (aka Quick Emulator), when built with the e1000e NIC emulation support, allows local guest OS privileged users to cause a denial of service (infinite loop) via vectors related to setting the initial receive / transmit descriptor head (TDH/RDH) outside the allocated descriptor buffer.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=4154c7e03fa55b4cf52509a83d50d6c09d743b7
- http://www.debian.org/security/2017/dsa-3920
- http://www.securityfocus.com/bid/98766
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://security.gentoo.org/glsa/201706-03
- http://www.openwall.com/lists/oss-security/2017/05/31/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1452620
