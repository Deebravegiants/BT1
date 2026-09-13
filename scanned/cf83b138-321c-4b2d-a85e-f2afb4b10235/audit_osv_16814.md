# [H] CVE-2019-9852

## Summary
Severity: High
Advisory: CVE-2019-9852
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-15
Source: https://osv.dev/vulnerability/CVE-2019-9852
Type: osv

## Details
LibreOffice has a feature where documents can specify that pre-installed macros can be executed on various script events such as mouse-over, document-open etc. Access is intended to be restricted to scripts under the share/Scripts/python, user/Scripts/python sub-directories of the LibreOffice install. Protection was added, to address CVE-2018-16858, to avoid a directory traversal attack where scripts in arbitrary locations on the file system could be executed. However this new protection could be bypassed by a URL encoding attack. In the fixed versions, the parsed url describing the script location is correctly encoded before further processing. This issue affects: Document Foundation LibreOffice versions prior to 6.2.6.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PMEGUWMWORC3DOVEHVXLFT3A5RSCMLBH/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00067.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00005.html
- https://seclists.org/bugtraq/2019/Sep/17
- https://usn.ubuntu.com/4102-1/
- https://www.debian.org/security/2019/dsa-4501
- https://seclists.org/bugtraq/2019/Aug/28
- https://www.libreoffice.org/about-us/security/advisories/CVE-2019-9852
