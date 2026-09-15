# [C] CVE-2016-5118

## Summary
Severity: Critical
Advisory: CVE-2016-5118
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-10
Source: https://osv.dev/vulnerability/CVE-2016-5118
Type: osv

## Details
The OpenBlob function in blob.c in GraphicsMagick before 1.3.24 and ImageMagick allows remote attackers to execute arbitrary code via a | (pipe) character at the start of a filename.

## References
- http://hg.code.sf.net/p/graphicsmagick/code/rev/ae3928faa858
- http://git.imagemagick.org/repos/ImageMagick/commit/40639d173aa8c76b850d625c630b711fee4dcfb8
- http://hg.code.sf.net/p/graphicsmagick/code/file/41876934e762/ChangeLog
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00047.html
- http://www.debian.org/security/2016/dsa-3591
- http://www.debian.org/security/2016/dsa-3746
- http://www.openwall.com/lists/oss-security/2016/05/29/7
- http://www.openwall.com/lists/oss-security/2016/05/30/1
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/90938
- http://www.securitytracker.com/id/1035984
- http://www.securitytracker.com/id/1035985
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.397749
