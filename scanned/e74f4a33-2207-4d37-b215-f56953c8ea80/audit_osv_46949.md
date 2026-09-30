# [H] CVE-2015-8467

## Summary
Severity: High
Advisory: CVE-2015-8467
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2015-12-29
Source: https://osv.dev/vulnerability/CVE-2015-8467
Type: osv

## Details
The samldb_check_user_account_control_acl function in dsdb/samdb/ldb_modules/samldb.c in Samba 4.x before 4.1.22, 4.2.x before 4.2.7, and 4.3.x before 4.3.3 does not properly check for administrative privileges during creation of machine accounts, which allows remote authenticated users to bypass intended access restrictions by leveraging the existence of a domain with both a Samba DC and a Windows DC, a similar issue to CVE-2015-2535.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00042.html
- http://www.debian.org/security/2016/dsa-3433
- http://www.securityfocus.com/bid/79735
- http://www.securitytracker.com/id/1034493
- http://www.ubuntu.com/usn/USN-2855-1
- http://www.ubuntu.com/usn/USN-2855-2
- https://bugzilla.redhat.com/show_bug.cgi?id=1290294
- https://security.gentoo.org/glsa/201612-47
- https://www.samba.org/samba/security/CVE-2015-8467.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00042.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1290294
- https://git.samba.org/?p=samba.git%3Ba=commit%3Bh=b000da128b5fb519d2d3f2e7fd20e4a25b7dae7d
