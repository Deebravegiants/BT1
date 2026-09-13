# [H] CVE-2021-33477

## Summary
Severity: High
Advisory: CVE-2021-33477
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2021-33477
Type: osv

## Details
rxvt-unicode 9.22, rxvt 2.7.10, mrxvt 0.5.4, and Eterm 0.9.7 allow (potentially remote) code execution because of improper handling of certain escape sequences (ESC G Q). A response is terminated by a newline.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6RFMU5YXXNYYVA7G2DAHRXXHO6JKVFUT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AO52OLNOOKOCZSJCN3R7Q25XA32BWNWP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DUV4LDVZVW7KCGPAMFZD4ZJ4FVLPOX4C/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NZWGE2RJONBEHSPCBUAW72NTRTIFKZAX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SLPVEPBH37EBR4R54RMC6GD33J37HJXD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UXAKO6N6NKTR6Z6KVAPEXSZQMRU52SGA/
- http://cvs.schmorp.de/rxvt-unicode/Changes?view=log
- https://git.enlightenment.org/apps/eterm.git/log/
- https://lists.debian.org/debian-lts-announce/2021/05/msg00026.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00012.html
- https://security.gentoo.org/glsa/202105-17
- https://security.gentoo.org/glsa/202209-07
- https://sourceforge.net/projects/materm/files/mrxvt%20source/
- https://sourceforge.net/projects/rxvt/files/rxvt-dev/
- https://www.openwall.com/lists/oss-security/2017/05/01/20
- http://cvs.schmorp.de/rxvt-unicode/src/command.C?r1=1.582&r2=1.583
- https://packetstormsecurity.com/files/162621/rxvt-2.7.0-rxvt-unicode-9.22-Code-Execution.html
- https://www.openwall.com/lists/oss-security/2021/05/17/1
