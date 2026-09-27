# [M] CVE-2009-5078

## Summary
Severity: Medium
Advisory: CVE-2009-5078
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2011-06-30
Source: https://osv.dev/vulnerability/CVE-2009-5078
Type: osv

## Details
contrib/pdfmark/pdfroff.sh in GNU troff (aka groff) before 1.21 launches the Ghostscript program without the -dSAFER option, which allows remote attackers to create, overwrite, rename, or delete arbitrary files via a crafted document.

## References
- http://lists.apple.com/archives/security-announce/2015/Aug/msg00001.html
- https://support.apple.com/kb/HT205031
- ftp://ftp.gnu.org/gnu/groff/groff-1.20.1-1.21.diff.gz
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=538338
- http://openwall.com/lists/oss-security/2009/08/09/1
- http://openwall.com/lists/oss-security/2009/08/10/2
- http://www.securityfocus.com/bid/36381
