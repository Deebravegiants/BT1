# [M] CVE-2020-15706

## Summary
Severity: Medium
Advisory: CVE-2020-15706
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-29
Source: https://osv.dev/vulnerability/CVE-2020-15706
Type: osv

## Details
GRUB2 contains a race condition in grub_script_function_create() leading to a use-after-free vulnerability which can be triggered by redefining a function whilst the same function is already executing, leading to arbitrary code execution and secure boot restriction bypass. This issue affects GRUB2 version 2.04 and prior versions.

## References
- http://ubuntu.com/security/notices/USN-4432-1
- https://security.gentoo.org/glsa/202104-05
- https://www.eclypsium.com/2020/07/29/theres-a-hole-in-the-boot/
- https://www.openwall.com/lists/oss-security/2020/07/29/3
- https://www.suse.com/support/kb/doc/?id=000019673
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00016.html
- https://access.redhat.com/security/vulnerabilities/grub2bootloader
- https://security.netapp.com/advisory/ntap-20200731-0008/
- https://wiki.ubuntu.com/SecurityTeam/KnowledgeBase/GRUB2SecureBootBypass
- https://www.debian.org/security/2020-GRUB-UEFI-SecureBoot
- https://www.debian.org/security/2020/dsa-4735
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00017.html
- http://www.openwall.com/lists/oss-security/2020/07/29/3
- https://usn.ubuntu.com/4432-1/
- https://www.suse.com/c/suse-addresses-grub2-secure-boot-issue/
- https://lists.gnu.org/archive/html/grub-devel/2020-07/msg00034.html
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV200011
