# [M] CVE-2011-2684

## Summary
Severity: Medium
Advisory: CVE-2011-2684
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-10-23
Source: https://osv.dev/vulnerability/CVE-2011-2684
Type: osv

## Details
foo2zjs before 20110722dfsg-3ubuntu1 as packaged in Ubuntu, 20110722dfsg-1 as packaged in Debian unstable, and 20090908dfsg-5.1+squeeze0 as packaged in Debian squeeze create temporary files insecurely, which allows local users to write over arbitrary files via a symlink attack on /tmp/foo2zjs.

## References
- http://www.openwall.com/lists/oss-security/2011/07/06/10
- http://www.openwall.com/lists/oss-security/2014/02/08/5
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=633870
- https://bugs.launchpad.net/ubuntu/+source/foo2zjs/+bug/805370
- https://security-tracker.debian.org/tracker/CVE-2011-2684/
- http://www.openwall.com/lists/oss-security/2011/07/06/10
- http://www.openwall.com/lists/oss-security/2014/02/08/5
