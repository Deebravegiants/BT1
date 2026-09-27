# [M] CVE-2020-15707

## Summary
Severity: Medium
Advisory: CVE-2020-15707
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-29
Source: https://osv.dev/vulnerability/CVE-2020-15707
Type: osv

## Details
Integer overflows were discovered in the functions grub_cmd_initrd and grub_initrd_init in the efilinux component of GRUB2, as shipped in Debian, Red Hat, and Ubuntu (the functionality is not included in GRUB2 upstream), leading to a heap-based buffer overflow. These could be triggered by an extremely large number of arguments to the initrd command on 32-bit architectures, or a crafted filesystem with very large files on any architecture. An attacker could use this to execute arbitrary code and bypass UEFI Secure Boot restrictions. This issue affects GRUB2 version 2.04 and prior versions.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00017.html
- http://ubuntu.com/security/notices/USN-4432-1
- https://security.netapp.com/advisory/ntap-20200731-0008/
- https://usn.ubuntu.com/4432-1/
- https://www.suse.com/support/kb/doc/?id=000019673
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00016.html
- http://www.openwall.com/lists/oss-security/2020/07/29/3
- https://wiki.ubuntu.com/SecurityTeam/KnowledgeBase/GRUB2SecureBootBypass
- https://www.debian.org/security/2020-GRUB-UEFI-SecureBoot
- https://www.debian.org/security/2020/dsa-4735
- https://www.suse.com/c/suse-addresses-grub2-secure-boot-issue/
- https://access.redhat.com/security/vulnerabilities/grub2bootloader
- https://security.gentoo.org/glsa/202104-05
- https://www.openwall.com/lists/oss-security/2020/07/29/3
- https://lists.gnu.org/archive/html/grub-devel/2020-07/msg00034.html
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV200011
- https://www.eclypsium.com/2020/07/29/theres-a-hole-in-the-boot/
