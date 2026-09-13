# [H] CVE-2015-1395

## Summary
Severity: High
Advisory: CVE-2015-1395
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-08-25
Source: https://osv.dev/vulnerability/CVE-2015-1395
Type: osv

## Details
Directory traversal vulnerability in GNU patch versions which support Git-style patching before 2.7.3 allows remote attackers to write to arbitrary files with the permissions of the target user via a .. (dot dot) in a diff file name.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-April/154214.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-January/148953.html
- http://www.openwall.com/lists/oss-security/2015/01/27/28
- http://www.securityfocus.com/bid/72846
- http://www.ubuntu.com/usn/USN-2651-1
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=775873
- https://bugzilla.redhat.com/show_bug.cgi?id=1184490
- https://savannah.gnu.org/bugs/?44059
- http://www.openwall.com/lists/oss-security/2015/01/27/28
- http://lists.fedoraproject.org/pipermail/package-announce/2015-April/154214.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-January/148953.html
- http://www.openwall.com/lists/oss-security/2015/01/27/28
- http://www.ubuntu.com/usn/USN-2651-1
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=775873
- https://bugzilla.redhat.com/show_bug.cgi?id=1184490
- https://git.savannah.gnu.org/cgit/patch.git/commit/?id=17953b5893f7c9835f0dd2a704ba04e0371d2cbd
- https://savannah.gnu.org/bugs/?44059
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=775873
- https://bugzilla.redhat.com/show_bug.cgi?id=1184490
- https://git.savannah.gnu.org/cgit/patch.git/commit/?id=17953b5893f7c9835f0dd2a704ba04e0371d2cbd
