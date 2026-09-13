# [H] CVE-2016-0728

## Summary
Severity: High
Advisory: CVE-2016-0728
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-02-08
Source: https://osv.dev/vulnerability/CVE-2016-0728
Type: osv

## Details
The join_session_keyring function in security/keys/process_keys.c in the Linux kernel before 4.4.1 mishandles object references in a certain error case, which allows local users to gain privileges or cause a denial of service (integer overflow and use-after-free) via crafted keyctl commands.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/176194.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00034.html
- http://rhn.redhat.com/errata/RHSA-2016-0064.html
- http://rhn.redhat.com/errata/RHSA-2016-0068.html
- http://www.openwall.com/lists/oss-security/2016/01/19/2
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securitytracker.com/id/1034701
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=23567fd052a9abb6d67fe8e7a9ccdd9800a540f2
- http://www.ubuntu.com/usn/USN-2870-2
- https://security.netapp.com/advisory/ntap-20160211-0001/
- http://www.securityfocus.com/bid/81054
- http://www.ubuntu.com/usn/USN-2872-2
- http://www.ubuntu.com/usn/USN-2872-3
- https://bto.bluecoat.com/security-advisory/sa112
- https://h20565.www2.hp.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05018265
- https://www.exploit-db.com/exploits/39277/
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176484.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00045.html
