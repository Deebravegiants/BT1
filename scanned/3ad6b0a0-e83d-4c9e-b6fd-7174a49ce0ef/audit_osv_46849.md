# [M] CVE-2015-5700

## Summary
Severity: Medium
Advisory: CVE-2015-5700
CVSS: 6.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2017-08-25
Source: https://osv.dev/vulnerability/CVE-2015-5700
Type: osv

## Details
mktexlsr revision 22855 through revision 36625 as packaged in texlive allows local users to write to arbitrary files via a symlink attack.

## References
- http://www.openwall.com/lists/oss-security/2015/07/30/6
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=775139
- https://bugzilla.redhat.com/show_bug.cgi?id=1181167
- https://www.tug.org/svn/texlive/trunk/Build/source/texk/kpathsea/mktexlsr?r1=19613&r2=22885
- https://www.tug.org/svn/texlive/trunk/Build/source/texk/kpathsea/mktexlsr?view=log
- http://www.openwall.com/lists/oss-security/2015/07/30/6
- https://bugzilla.redhat.com/show_bug.cgi?id=1181167
- https://www.tug.org/svn/texlive/trunk/Build/source/texk/kpathsea/mktexlsr?r1=19613&r2=22885
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=775139
- https://bugzilla.redhat.com/show_bug.cgi?id=1181167
- https://usn.ubuntu.com/3788-1/
