# [M] CVE-2015-1607

## Summary
Severity: Medium
Advisory: CVE-2015-1607
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-20
Source: https://osv.dev/vulnerability/CVE-2015-1607
Type: osv

## Details
kbx/keybox-search.c in GnuPG before 1.4.19, 2.0.x before 2.0.27, and 2.1.x before 2.1.2 does not properly handle bitwise left-shifts, which allows remote attackers to cause a denial of service (invalid read operation) via a crafted keyring file, related to sign extensions and "memcpy with overlapping ranges."

## References
- http://www.openwall.com/lists/oss-security/2015/02/13/14
- http://www.openwall.com/lists/oss-security/2015/02/14/6
- http://www.securityfocus.com/bid/72610
- http://www.ubuntu.com/usn/usn-2554-1/
- https://blog.fuzzing-project.org/5-Multiple-issues-in-GnuPG-found-through-keyring-fuzzing-TFPA-0012015.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000361.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000362.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000363.html
- http://www.openwall.com/lists/oss-security/2015/02/13/14
- http://www.openwall.com/lists/oss-security/2015/02/14/6
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000361.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000362.html
- https://lists.gnupg.org/pipermail/gnupg-announce/2015q1/000363.html
- http://git.gnupg.org/cgi-bin/gitweb.cgi?p=gnupg.git%3Ba=commit%3Bh=2183683bd633818dd031b090b5530951de76f392
