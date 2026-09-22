# [H] CVE-2017-5899

## Summary
Severity: High
Advisory: CVE-2017-5899
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-27
Source: https://osv.dev/vulnerability/CVE-2017-5899
Type: osv

## Details
Directory traversal vulnerability in the setuid root helper binary in S-nail (later S-mailx) before 14.8.16 allows local users to write to arbitrary files and consequently gain root privileges via a .. (dot dot) in the randstr argument.

## References
- https://www.mail-archive.com/s-nail-users%40lists.sourceforge.net/msg00551.html
- http://www.openwall.com/lists/oss-security/2017/02/07/4
- http://www.securityfocus.com/bid/96138
- http://www.openwall.com/lists/oss-security/2017/01/27/7
