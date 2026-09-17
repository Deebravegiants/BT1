# [M] CVE-2011-2902

## Summary
Severity: Medium
Advisory: CVE-2011-2902
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-01-30
Source: https://osv.dev/vulnerability/CVE-2011-2902
Type: osv

## Details
zxpdf in xpdf before 3.02-19 as packaged in Debian unstable and 3.02-12+squeeze1 as packaged in Debian squeeze deletes temporary files insecurely, which allows remote attackers to delete arbitrary files via a crafted .pdf.gz file name.

## References
- http://www.openwall.com/lists/oss-security/2014/02/08/5
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=635849
- https://security-tracker.debian.org/tracker/CVE-2011-2902/
- http://www.openwall.com/lists/oss-security/2014/02/08/5
