# [M] CVE-2015-8745

## Summary
Severity: Medium
Advisory: CVE-2015-8745
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2015-8745
Type: osv

## Details
QEMU (aka Quick Emulator) built with a VMWARE VMXNET3 paravirtual NIC emulator support is vulnerable to crash issue. It could occur while reading Interrupt Mask Registers (IMR). A privileged (CAP_SYS_RAWIO) guest user could use this flaw to crash the QEMU process instance resulting in DoS.

## References
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2016/01/04/4
- http://www.openwall.com/lists/oss-security/2016/01/04/7
- http://www.securityfocus.com/bid/79822
- http://www.securitytracker.com/id/1034575
- https://security.gentoo.org/glsa/201602-01
- http://www.openwall.com/lists/oss-security/2016/01/04/4
- http://www.openwall.com/lists/oss-security/2016/01/04/7
- https://bugzilla.redhat.com/show_bug.cgi?id=1270876
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=c6048f849c7e3f009786df76206e895
