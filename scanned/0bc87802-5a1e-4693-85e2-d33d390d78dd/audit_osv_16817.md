# [C] CVE-2019-9855

## Summary
Severity: Critical
Advisory: CVE-2019-9855
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-9855
Type: osv

## Details
LibreOffice is typically bundled with LibreLogo, a programmable turtle vector graphics script, which can execute arbitrary python commands contained with the document it is launched from. LibreOffice also has a feature where documents can specify that pre-installed scripts can be executed on various document script events such as mouse-over, etc. Protection was added to block calling LibreLogo from script event handers. However a Windows 8.3 path equivalence handling flaw left LibreOffice vulnerable under Windows that a document could trigger executing LibreLogo via a Windows filename pseudonym. This issue affects: Document Foundation LibreOffice 6.2 versions prior to 6.2.7; 6.3 versions prior to 6.3.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00067.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00055.html
- https://www.libreoffice.org/about-us/security/advisories/CVE-2019-9855/
