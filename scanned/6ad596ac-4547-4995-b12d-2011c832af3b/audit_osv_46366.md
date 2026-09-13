# [H] CVE-2005-4890

## Summary
Severity: High
Advisory: CVE-2005-4890
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-04
Source: https://osv.dev/vulnerability/CVE-2005-4890
Type: osv

## Details
There is a possible tty hijacking in shadow 4.x before 4.1.5 and sudo 1.x before 1.7.4 via "su - user -c program". The user session can be escaped to the parent session by using the TIOCSTI ioctl to push characters into the input buffer to be read by the next process.

## References
- http://www.openwall.com/lists/oss-security/2012/11/06/8
- http://www.openwall.com/lists/oss-security/2013/05/20/3
- http://www.openwall.com/lists/oss-security/2013/11/28/10
- http://www.openwall.com/lists/oss-security/2013/11/29/5
- http://www.openwall.com/lists/oss-security/2014/10/20/9
- http://www.openwall.com/lists/oss-security/2014/10/21/1
- http://www.openwall.com/lists/oss-security/2014/12/15/5
- http://www.openwall.com/lists/oss-security/2016/02/25/6
- https://access.redhat.com/security/cve/cve-2005-4890
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2005-4890
- https://security-tracker.debian.org/tracker/CVE-2005-4890
- http://www.openwall.com/lists/oss-security/2012/11/06/8
- http://www.openwall.com/lists/oss-security/2013/05/20/3
- http://www.openwall.com/lists/oss-security/2013/11/28/10
- http://www.openwall.com/lists/oss-security/2013/11/29/5
- http://www.openwall.com/lists/oss-security/2014/10/20/9
- http://www.openwall.com/lists/oss-security/2014/10/21/1
- http://www.openwall.com/lists/oss-security/2014/12/15/5
- http://www.openwall.com/lists/oss-security/2016/02/25/6
- http://www.openwall.com/lists/oss-security/2016/02/25/6
