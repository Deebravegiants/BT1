# [C] CVE-2019-9848

## Summary
Severity: Critical
Advisory: CVE-2019-9848
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-9848
Type: osv

## Details
LibreOffice has a feature where documents can specify that pre-installed scripts can be executed on various document events such as mouse-over, etc. LibreOffice is typically also bundled with LibreLogo, a programmable turtle vector graphics script, which can be manipulated into executing arbitrary python commands. By using the document event feature to trigger LibreLogo to execute python contained within a document a malicious document could be constructed which would execute arbitrary python commands silently without warning. In the fixed versions, LibreLogo cannot be called from a document event handler. This issue affects: Document Foundation LibreOffice versions prior to 6.2.5.

## References
- http://www.securityfocus.com/bid/109374
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PMEGUWMWORC3DOVEHVXLFT3A5RSCMLBH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XPTZJCNN52VNGSVC5DFKVW3EDMRDWKMP/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00067.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00005.html
- https://seclists.org/bugtraq/2019/Aug/28
- https://security.gentoo.org/glsa/201908-13
- https://usn.ubuntu.com/4063-1/
- https://www.libreoffice.org/about-us/security/advisories/CVE-2019-9848
