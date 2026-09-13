# [M] CVE-2015-8744

## Summary
Severity: Medium
Advisory: CVE-2015-8744
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2015-8744
Type: osv

## Details
QEMU (aka Quick Emulator) built with a VMWARE VMXNET3 paravirtual NIC emulator support is vulnerable to crash issue. It occurs when a guest sends a Layer-2 packet smaller than 22 bytes. A privileged (CAP_SYS_RAWIO) guest user could use this flaw to crash the QEMU process instance resulting in DoS.

## References
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2016/01/04/3
- http://www.openwall.com/lists/oss-security/2016/01/04/6
- http://www.securityfocus.com/bid/79821
- http://www.securitytracker.com/id/1034576
- https://bugzilla.redhat.com/show_bug.cgi?id=1270871
- https://security.gentoo.org/glsa/201602-01
- http://www.openwall.com/lists/oss-security/2016/01/04/3
- http://www.openwall.com/lists/oss-security/2016/01/04/6
- https://bugzilla.redhat.com/show_bug.cgi?id=1270871
- http://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=a7278b36fcab9af469563bd7b
