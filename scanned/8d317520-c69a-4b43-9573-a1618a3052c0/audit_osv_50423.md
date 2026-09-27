# [M] CVE-2020-15705

## Summary
Severity: Medium
Advisory: CVE-2020-15705
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-29
Source: https://osv.dev/vulnerability/CVE-2020-15705
Type: osv

## Details
GRUB2 fails to validate kernel signature when booted directly without shim, allowing secure boot to be bypassed. This only affects systems where the kernel signing certificate has been imported directly into the secure boot database and the GRUB image is booted directly without the use of shim. This issue affects GRUB2 version 2.04 and prior versions.

## References
- http://www.openwall.com/lists/oss-security/2021/03/02/3
- http://www.openwall.com/lists/oss-security/2021/09/17/2
- https://security.netapp.com/advisory/ntap-20200731-0008/
- https://www.suse.com/support/kb/doc/?id=000019673
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00067.html
- https://access.redhat.com/security/vulnerabilities/grub2bootloader
- https://wiki.ubuntu.com/SecurityTeam/KnowledgeBase/GRUB2SecureBootBypass
- https://www.debian.org/security/2020-GRUB-UEFI-SecureBoot
- https://www.eclypsium.com/2020/07/29/theres-a-hole-in-the-boot/
- https://www.openwall.com/lists/oss-security/2020/07/29/3
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00069.html
- http://ubuntu.com/security/notices/USN-4432-1
- http://www.openwall.com/lists/oss-security/2020/07/29/3
- http://www.openwall.com/lists/oss-security/2021/09/17/4
- http://www.openwall.com/lists/oss-security/2021/09/21/1
- https://security.gentoo.org/glsa/202104-05
- https://usn.ubuntu.com/4432-1/
- https://www.suse.com/c/suse-addresses-grub2-secure-boot-issue/
- https://lists.gnu.org/archive/html/grub-devel/2020-07/msg00034.html
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV200011
