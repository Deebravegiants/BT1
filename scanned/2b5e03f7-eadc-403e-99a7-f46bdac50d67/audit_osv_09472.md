# [H] CVE-2017-0358

## Summary
Severity: High
Advisory: CVE-2017-0358
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-13
Source: https://osv.dev/vulnerability/CVE-2017-0358
Type: osv

## Details
Jann Horn of Google Project Zero discovered that NTFS-3G, a read-write NTFS driver for FUSE, does not scrub the environment before executing modprobe with elevated privileges. A local user can take advantage of this flaw for local root privilege escalation.

## References
- http://www.openwall.com/lists/oss-security/2017/02/04/1
- http://www.securityfocus.com/bid/95987
- https://security.gentoo.org/glsa/201702-10
- https://www.debian.org/security/2017/dsa-3780
- https://marc.info/?l=oss-security&m=148594671929354&w=2
- https://www.exploit-db.com/exploits/41240/
- https://www.exploit-db.com/exploits/41356/
