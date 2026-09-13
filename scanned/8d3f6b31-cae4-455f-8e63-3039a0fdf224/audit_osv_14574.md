# [C] CVE-2019-10149

## Summary
Severity: Critical
Advisory: CVE-2019-10149
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-05
Source: https://osv.dev/vulnerability/CVE-2019-10149
Type: osv

## Details
A flaw was found in Exim versions 4.87 to 4.91 (inclusive). Improper validation of recipient address in deliver_message() function in /src/deliver.c may lead to remote command execution.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-10149
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00020.html
- http://seclists.org/fulldisclosure/2019/Jun/16
- http://www.openwall.com/lists/oss-security/2019/06/05/2
- http://www.openwall.com/lists/oss-security/2019/07/25/6
- http://www.openwall.com/lists/oss-security/2019/07/25/7
- http://www.openwall.com/lists/oss-security/2019/07/26/4
- http://www.openwall.com/lists/oss-security/2021/05/04/7
- http://www.securityfocus.com/bid/108679
- https://seclists.org/bugtraq/2019/Jun/5
- https://security.gentoo.org/glsa/201906-01
- https://usn.ubuntu.com/4010-1/
- https://www.debian.org/security/2019/dsa-4456
- https://www.exim.org/static/doc/security/CVE-2019-10149.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10149
- http://www.openwall.com/lists/oss-security/2019/06/05/3
- http://packetstormsecurity.com/files/153218/Exim-4.9.1-Remote-Command-Execution.html
- http://packetstormsecurity.com/files/153312/Exim-4.91-Local-Privilege-Escalation.html
- http://packetstormsecurity.com/files/154198/Exim-4.91-Local-Privilege-Escalation.html
- http://www.openwall.com/lists/oss-security/2019/06/05/4
