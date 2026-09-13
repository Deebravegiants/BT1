# [M] CVE-2019-9849

## Summary
Severity: Medium
Advisory: CVE-2019-9849
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-9849
Type: osv

## Details
LibreOffice has a 'stealth mode' in which only documents from locations deemed 'trusted' are allowed to retrieve remote resources. This mode is not the default mode, but can be enabled by users who want to disable LibreOffice's ability to include remote resources within a document. A flaw existed where bullet graphics were omitted from this protection prior to version 6.2.5. This issue affects: Document Foundation LibreOffice versions prior to 6.2.5.

## References
- http://www.securityfocus.com/bid/109374
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PMEGUWMWORC3DOVEHVXLFT3A5RSCMLBH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XPTZJCNN52VNGSVC5DFKVW3EDMRDWKMP/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00067.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00005.html
- https://security.gentoo.org/glsa/201908-13
- https://usn.ubuntu.com/4063-1/
- https://www.libreoffice.org/about-us/security/advisories/CVE-2019-9849
