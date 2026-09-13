# [H] CVE-2021-33285

## Summary
Severity: High
Advisory: CVE-2021-33285
Aliases: CVE-2021-33286, CVE-2021-33287, CVE-2021-33289, CVE-2021-35266, CVE-2021-35267, CVE-2021-35268, CVE-2021-39251, CVE-2021-39252
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-33285
Type: osv

## Details
In NTFS-3G versions < 2021.8.22, when a specially crafted NTFS attribute is supplied to the function ntfs_get_attribute_value, a heap buffer overflow can occur allowing for memory disclosure or denial of service. The vulnerability is caused by an out-of-bound buffer access which can be triggered by mounting a crafted ntfs partition. The root cause is a missing consistency check after reading an MFT record : the "bytes_in_use" field should be less than the "bytes_allocated" field. When it is not, the parsing of the records proceeds into the wild.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/766ISTT3KCARKFUIQT7N6WV6T63XOKG3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HSEKTKHO5HFZHWZNJNBJZA56472KRUZI/
- http://www.openwall.com/lists/oss-security/2021/08/30/1
- https://github.com/tuxera/ntfs-3g/security/advisories/GHSA-q759-8j5v-q5jp
- https://lists.debian.org/debian-lts-announce/2021/11/msg00013.html
- https://security.gentoo.org/glsa/202301-01
- https://www.debian.org/security/2021/dsa-4971
- https://www.openwall.com/lists/oss-security/2021/08/30/1
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=988386
- https://bugzilla.redhat.com/show_bug.cgi?id=2001608
