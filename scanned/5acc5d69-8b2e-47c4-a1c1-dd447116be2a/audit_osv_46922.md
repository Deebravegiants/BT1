# [H] CVE-2015-8106

## Summary
Severity: High
Advisory: CVE-2015-8106
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-04-18
Source: https://osv.dev/vulnerability/CVE-2015-8106
Type: osv

## Details
Format string vulnerability in the CmdKeywords function in funct1.c in latex2rtf before 2.3.10 allows remote attackers to execute arbitrary code via format string specifiers in the \keywords command in a crafted TeX file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1282492
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181276.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181677.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/181725.html
- http://www.openwall.com/lists/oss-security/2015/11/16/3
- https://sourceforge.net/p/latex2rtf/code/1244/
