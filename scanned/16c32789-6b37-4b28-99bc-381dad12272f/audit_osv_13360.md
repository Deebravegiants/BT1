# [H] CVE-2018-19518

## Summary
Severity: High
Advisory: CVE-2018-19518
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-25
Source: https://osv.dev/vulnerability/CVE-2018-19518
Type: osv

## Details
University of Washington IMAP Toolkit 2007f on UNIX, as used in imap_open() in PHP and other products, launches an rsh command (by means of the imap_rimap function in c-client/imap4r1.c and the tcp_aopen function in osdep/unix/tcp_unix.c) without preventing argument injection, which might allow remote attackers to execute arbitrary OS commands if the IMAP server name is untrusted input (e.g., entered by a user of a web application) and if rsh has been replaced by a program with different argument semantics. For example, if rsh is a link to ssh (as seen on Debian and Ubuntu systems), then the attack can use an IMAP server name containing a "-oProxyCommand" argument.

## References
- http://www.securityfocus.com/bid/106018
- http://www.securitytracker.com/id/1042157
- https://git.php.net/?p=php-src.git%3Ba=commit%3Bh=e5bfea64c81ae34816479bb05d17cdffe45adddb
- https://bugs.debian.org/913775
- https://bugs.debian.org/913835
- https://bugs.debian.org/913836
- https://bugs.php.net/bug.php?id=77160
- https://lists.debian.org/debian-lts-announce/2018/12/msg00006.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00031.html
- https://security.gentoo.org/glsa/202003-57
- https://security.netapp.com/advisory/ntap-20181221-0004/
- https://usn.ubuntu.com/4160-1/
- https://www.debian.org/security/2018/dsa-4353
- https://antichat.com/threads/463395/#post-4254681
- https://bugs.php.net/bug.php?id=76428
- https://bugs.php.net/bug.php?id=77153
- https://github.com/Bo0oM/PHP_imap_open_exploit/blob/master/exploit.php
- https://www.exploit-db.com/exploits/45914/
- https://www.openwall.com/lists/oss-security/2018/11/22/3
