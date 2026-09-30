# [H] CVE-2019-9854

## Summary
Severity: High
Advisory: CVE-2019-9854
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-09-06
Source: https://osv.dev/vulnerability/CVE-2019-9854
Type: osv

## Details
LibreOffice has a feature where documents can specify that pre-installed macros can be executed on various script events such as mouse-over, document-open etc. Access is intended to be restricted to scripts under the share/Scripts/python, user/Scripts/python sub-directories of the LibreOffice install. Protection was added, to address CVE-2019-9852, to avoid a directory traversal attack where scripts in arbitrary locations on the file system could be executed by employing a URL encoding attack to defeat the path verification step. However this protection could be bypassed by taking advantage of a flaw in how LibreOffice assembled the final script URL location directly from components of the passed in path as opposed to solely from the sanitized output of the path verification step. This issue affects: Document Foundation LibreOffice 6.2 versions prior to 6.2.7; 6.3 versions prior to 6.3.1.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XQKKOIY2DMZCXJINOLIQXD2NWISDKK3N/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00067.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00055.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1769907
- https://lists.debian.org/debian-lts-announce/2019/10/msg00005.html
- https://seclists.org/bugtraq/2019/Sep/17
- https://usn.ubuntu.com/4138-1/
- https://www.debian.org/security/2019/dsa-4519
- https://www.libreoffice.org/about-us/security/advisories/CVE-2019-9854/
