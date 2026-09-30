# [C] CVE-2015-7545

## Summary
Severity: Critical
Advisory: CVE-2015-7545
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2015-7545
Type: osv

## Details
The (1) git-remote-ext and (2) unspecified other remote helper programs in Git before 2.3.10, 2.4.x before 2.4.10, 2.5.x before 2.5.4, and 2.6.x before 2.6.1 do not properly restrict the allowed protocols, which might allow remote attackers to execute arbitrary code via a URL in a (a) .gitmodules file or (b) unknown other sources in a submodule.

## References
- http://rhn.redhat.com/errata/RHSA-2015-2515.html
- http://www.debian.org/security/2016/dsa-3435
- http://www.ubuntu.com/usn/USN-2835-1
- https://github.com/git/git/blob/master/Documentation/RelNotes/2.3.10.txt
- https://github.com/git/git/blob/master/Documentation/RelNotes/2.4.10.txt
- https://github.com/git/git/blob/master/Documentation/RelNotes/2.5.4.txt
- https://security.gentoo.org/glsa/201605-01
- https://github.com/git/git/blob/master/Documentation/RelNotes/2.3.10.txt
- https://github.com/git/git/blob/master/Documentation/RelNotes/2.4.10.txt
- https://github.com/git/git/blob/master/Documentation/RelNotes/2.5.4.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=1269794
- http://lists.opensuse.org/opensuse-updates/2015-11/msg00066.html
- http://www.openwall.com/lists/oss-security/2015/12/08/5
- http://www.openwall.com/lists/oss-security/2015/12/09/8
- http://www.openwall.com/lists/oss-security/2015/12/11/7
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
- http://www.securityfocus.com/bid/78711
- http://www.securitytracker.com/id/1034501
