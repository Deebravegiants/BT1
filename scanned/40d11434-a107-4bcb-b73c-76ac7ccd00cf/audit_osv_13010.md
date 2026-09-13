# [C] CVE-2018-16858

## Summary
Severity: Critical
Advisory: CVE-2018-16858
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2018-16858
Type: osv

## Details
It was found that libreoffice before versions 6.0.7 and 6.1.3 was vulnerable to a directory traversal attack which could be used to execute arbitrary macros bundled with a document. An attacker could craft a document, which when opened by LibreOffice, would execute a Python method from a script in any arbitrary file system location, specified relative to the LibreOffice install location.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00059.html
- https://seclists.org/bugtraq/2019/Aug/28
- http://www.rapid7.com/db/modules/exploit/multi/fileformat/libreoffice_macro_exec
- https://access.redhat.com/errata/RHSA-2019:2130
- https://www.libreoffice.org/about-us/security/advisories/cve-2018-16858/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16858
- http://packetstormsecurity.com/files/152560/LibreOffice-Macro-Code-Execution.html
- https://www.exploit-db.com/exploits/46727/
