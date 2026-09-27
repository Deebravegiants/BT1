# [H] CVE-2015-5330

## Summary
Severity: High
Advisory: CVE-2015-5330
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2015-12-29
Source: https://osv.dev/vulnerability/CVE-2015-5330
Type: osv

## Details
ldb before 1.1.24, as used in the AD LDAP server in Samba 4.x before 4.1.22, 4.2.x before 4.2.7, and 4.3.x before 4.3.3, mishandles string lengths, which allows remote attackers to obtain sensitive information from daemon heap memory by sending crafted packets and then reading (1) an error message or (2) a database value.

## References
- http://www.debian.org/security/2016/dsa-3433
- http://www.ubuntu.com/usn/USN-2855-1
- http://www.ubuntu.com/usn/USN-2855-2
- http://www.ubuntu.com/usn/USN-2856-1
- https://security.gentoo.org/glsa/201612-47
- https://www.samba.org/samba/security/CVE-2015-5330.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1281326
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00048.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/79734
- http://www.securitytracker.com/id/1034493
- https://git.samba.org/?p=samba.git%3Ba=commit%3Bh=0454b95657846fcecf0f51b6f1194faac02518bd
