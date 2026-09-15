# [H] CVE-2015-7540

## Summary
Severity: High
Advisory: CVE-2015-7540
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2015-12-29
Source: https://osv.dev/vulnerability/CVE-2015-7540
Type: osv

## Details
The LDAP server in the AD domain controller in Samba 4.x before 4.1.22 does not check return values to ensure successful ASN.1 memory allocation, which allows remote attackers to cause a denial of service (memory consumption and daemon crash) via crafted packets.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/174076.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/174391.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00033.html
- http://www.debian.org/security/2016/dsa-3433
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/79736
- http://www.securitytracker.com/id/1034492
- http://www.ubuntu.com/usn/USN-2855-1
- http://www.ubuntu.com/usn/USN-2855-2
- https://bugzilla.redhat.com/show_bug.cgi?id=1288451
- https://security.gentoo.org/glsa/201612-47
- https://www.samba.org/samba/security/CVE-2015-7540.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00033.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1288451
- https://git.samba.org/?p=samba.git%3Ba=commit%3Bh=530d50a1abdcdf4d1775652d4c456c1274d83d8d
- https://git.samba.org/?p=samba.git%3Ba=commit%3Bh=9d989c9dd7a5b92d0c5d65287935471b83b6e884
