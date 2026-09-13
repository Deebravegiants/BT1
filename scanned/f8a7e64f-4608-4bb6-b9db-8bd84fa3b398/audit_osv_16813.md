# [C] CVE-2019-9851

## Summary
Severity: Critical
Advisory: CVE-2019-9851
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/CVE-2019-9851
Type: osv

## Details
LibreOffice is typically bundled with LibreLogo, a programmable turtle vector graphics script, which can execute arbitrary python commands contained with the document it is launched from. Protection was added, to address CVE-2019-9848, to block calling LibreLogo from document event script handers, e.g. mouse over. However LibreOffice also has a separate feature where documents can specify that pre-installed scripts can be executed on various global script events such as document-open, etc. In the fixed versions, global script event handlers are validated equivalently to document script event handlers. This issue affects: Document Foundation LibreOffice versions prior to 6.2.6.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PMEGUWMWORC3DOVEHVXLFT3A5RSCMLBH/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00067.html
- http://packetstormsecurity.com/files/154168/LibreOffice-Macro-Python-Code-Execution.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00005.html
- https://seclists.org/bugtraq/2019/Aug/28
- https://usn.ubuntu.com/4102-1/
- https://www.debian.org/security/2019/dsa-4501
- https://www.libreoffice.org/about-us/security/advisories/CVE-2019-9851
