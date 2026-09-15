# [H] CVE-2017-8849

## Summary
Severity: High
Advisory: CVE-2017-8849
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-17
Source: https://osv.dev/vulnerability/CVE-2017-8849
Type: osv

## Details
smb4k before 2.0.1 allows local users to gain root privileges by leveraging failure to verify arguments to the mount helper DBUS service.

## References
- http://www.securityfocus.com/bid/98737
- https://www.kde.org/info/security/advisory-20170510-2.txt
- http://www.debian.org/security/2017/dsa-3951
- http://www.securityfocus.com/bid/98690
- https://security.gentoo.org/glsa/201705-14
- https://cgit.kde.org/smb4k.git/commit/?id=71554140bdaede27b95dbe4c9b5a028a83c83cce
- http://www.openwall.com/lists/oss-security/2017/05/10/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1449656
- https://cgit.kde.org/smb4k.git/commit/?id=a90289b0962663bc1d247bbbd31b9e65b2ca000e
- https://www.exploit-db.com/exploits/42053/
