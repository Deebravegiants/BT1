# [C] CVE-2019-9850

## Summary
Severity: Critical
Advisory: CVE-2019-9850
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/CVE-2019-9850
Type: osv

## Details
LibreOffice is typically bundled with LibreLogo, a programmable turtle vector graphics script, which can execute arbitrary python commands contained with the document it is launched from. LibreOffice also has a feature where documents can specify that pre-installed scripts can be executed on various document script events such as mouse-over, etc. Protection was added, to address CVE-2019-9848, to block calling LibreLogo from script event handers. However an insufficient url validation vulnerability in LibreOffice allowed malicious to bypass that protection and again trigger calling LibreLogo from script event handlers. This issue affects: Document Foundation LibreOffice versions prior to 6.2.6.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PMEGUWMWORC3DOVEHVXLFT3A5RSCMLBH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WVSDPZJG3UA43X3JXRHJAWXLDZEW77LM/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00067.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00005.html
- https://seclists.org/bugtraq/2019/Aug/28
- https://usn.ubuntu.com/4102-1/
- https://www.debian.org/security/2019/dsa-4501
- https://www.libreoffice.org/about-us/security/advisories/CVE-2019-9850
