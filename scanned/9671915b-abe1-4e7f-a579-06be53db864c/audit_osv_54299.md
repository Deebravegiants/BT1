# [H] CVE-2023-4692

## Summary
Severity: High
Advisory: CVE-2023-4692
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-4692
Type: osv

## Details
An out-of-bounds write flaw was found in grub2's NTFS filesystem driver. This issue may allow an attacker to present a specially crafted NTFS filesystem image, leading to grub's heap metadata corruption. In some circumstances, the attack may also corrupt the UEFI firmware heap metadata. As a result, arbitrary code execution and secure boot protection bypass may be achieved.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FUU42E7CPYLATXOYVYNW6YTXXULAOV6L/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OIRJ5UZRXX2KLR4IKBJEQUNGOCXMMDLY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PERFILCHFEUGG3OAMC6W55P6DDIBZK4Q/
- https://access.redhat.com/security/cve/CVE-2023-4692
- https://seclists.org/oss-sec/2023/q4/37
- https://security.gentoo.org/glsa/202311-14
- https://security.netapp.com/advisory/ntap-20231208-0002/
- https://access.redhat.com/errata/RHSA-2024:2456
- https://access.redhat.com/errata/RHSA-2024:3184
- https://bugzilla.redhat.com/show_bug.cgi?id=2236613
- https://lists.gnu.org/archive/html/grub-devel/2023-10/msg00028.html
- https://dfir.ru/2023/10/03/cve-2023-4692-cve-2023-4693-vulnerabilities-in-the-grub-boot-manager/
