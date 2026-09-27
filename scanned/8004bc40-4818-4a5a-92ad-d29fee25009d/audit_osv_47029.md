# [H] CVE-2015-8743

## Summary
Severity: High
Advisory: CVE-2015-8743
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2015-8743
Type: osv

## Details
QEMU (aka Quick Emulator) built with the NE2000 device emulation support is vulnerable to an OOB r/w access issue. It could occur while performing 'ioport' r/w operations. A privileged (CAP_SYS_RAWIO) user/process could use this flaw to leak or corrupt QEMU memory bytes.

## References
- http://www.debian.org/security/2016/dsa-3469
- http://www.debian.org/security/2016/dsa-3470
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2016/01/04/1
- http://www.openwall.com/lists/oss-security/2016/01/04/2
- http://www.securityfocus.com/bid/79820
- http://www.securitytracker.com/id/1034574
- https://lists.gnu.org/archive/html/qemu-devel/2016-01/msg00050.html
- https://security.gentoo.org/glsa/201602-01
- http://www.openwall.com/lists/oss-security/2016/01/04/1
- http://www.openwall.com/lists/oss-security/2016/01/04/2
- https://lists.gnu.org/archive/html/qemu-devel/2016-01/msg00050.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1264929
