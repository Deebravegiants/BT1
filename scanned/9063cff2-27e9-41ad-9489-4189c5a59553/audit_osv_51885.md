# [C] CVE-2021-44143

## Summary
Severity: Critical
Advisory: CVE-2021-44143
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-22
Source: https://osv.dev/vulnerability/CVE-2021-44143
Type: osv

## Details
A flaw was found in mbsync in isync 1.4.0 through 1.4.3. Due to an unchecked condition, a malicious or compromised IMAP server could use a crafted mail message that lacks headers (i.e., one that starts with an empty line) to provoke a heap overflow, which could conceivably be exploited for remote code execution.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CYZ2GNB4ZO2T27D2XNUWMCS3THZYSJQU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LCBSY7OZ57XNC6ZYXF6WU5KBSWITZVDX/
- https://security.gentoo.org/glsa/202208-15
- https://sourceforge.net/p/isync/isync/ref/master/tags/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=999804
- https://sourceforge.net/p/isync/isync/commit_browser
- http://www.openwall.com/lists/oss-security/2021/12/03/2
