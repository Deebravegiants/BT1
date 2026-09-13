# [M] CVE-2023-4693

## Summary
Severity: Medium
Advisory: CVE-2023-4693
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-4693
Type: osv

## Details
An out-of-bounds read flaw was found on grub2's NTFS filesystem driver. This issue may allow a physically present attacker to present a specially crafted NTFS file system image to read arbitrary memory locations. A successful attack allows sensitive data cached in memory or EFI variable values to be leaked, presenting a high Confidentiality risk.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FUU42E7CPYLATXOYVYNW6YTXXULAOV6L/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PERFILCHFEUGG3OAMC6W55P6DDIBZK4Q/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OIRJ5UZRXX2KLR4IKBJEQUNGOCXMMDLY/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00007.html
- https://access.redhat.com/security/cve/CVE-2023-4693
- https://seclists.org/oss-sec/2023/q4/37
- https://security.gentoo.org/glsa/202311-14
- https://security.netapp.com/advisory/ntap-20231208-0002/
- https://access.redhat.com/errata/RHSA-2024:2456
- https://access.redhat.com/errata/RHSA-2024:3184
- https://bugzilla.redhat.com/show_bug.cgi?id=2238343
- https://lists.gnu.org/archive/html/grub-devel/2023-10/msg00028.html
- https://dfir.ru/2023/10/03/cve-2023-4692-cve-2023-4693-vulnerabilities-in-the-grub-boot-manager/
