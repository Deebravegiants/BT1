# [C] CVE-2021-26937

## Summary
Severity: Critical
Advisory: CVE-2021-26937
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-09
Source: https://osv.dev/vulnerability/CVE-2021-26937
Type: osv

## Details
encoding.c in GNU Screen through 4.8.0 allows remote attackers to cause a denial of service (invalid write access and application crash) or possibly have unspecified other impact via a crafted UTF-8 character sequence.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GNWBOIDEPOEQS5RMQVMFKHKXJCGNYWBL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JJWLXP45POUUYBJRRWPVAWNZDJTLYWVM/
- https://ftp.gnu.org/gnu/screen/
- https://security.netapp.com/advisory/ntap-20250509-0004/
- https://security.gentoo.org/glsa/202105-11
- https://lists.debian.org/debian-lts-announce/2021/02/msg00031.html
- https://www.debian.org/security/2021/dsa-4861
- http://www.openwall.com/lists/oss-security/2021/02/09/8
- https://lists.gnu.org/archive/html/screen-devel/2021-02/msg00000.html
- https://www.openwall.com/lists/oss-security/2021/02/09/3
