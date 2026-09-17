# [H] CVE-2021-35269

## Summary
Severity: High
Advisory: CVE-2021-35269
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-35269
Type: osv

## Details
NTFS-3G versions < 2021.8.22, when a specially crafted NTFS attribute from the MFT is setup in the function ntfs_attr_setup_flag, a heap buffer overflow can occur allowing for code execution and escalation of privileges.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/766ISTT3KCARKFUIQT7N6WV6T63XOKG3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HSEKTKHO5HFZHWZNJNBJZA56472KRUZI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/766ISTT3KCARKFUIQT7N6WV6T63XOKG3/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HSEKTKHO5HFZHWZNJNBJZA56472KRUZI/
- http://www.openwall.com/lists/oss-security/2021/08/30/1
- https://lists.debian.org/debian-lts-announce/2021/11/msg00013.html
- https://security.gentoo.org/glsa/202301-01
- https://www.debian.org/security/2021/dsa-4971
