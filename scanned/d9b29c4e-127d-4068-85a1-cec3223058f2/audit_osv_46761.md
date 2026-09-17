# [M] CVE-2015-1606

## Summary
Severity: Medium
Advisory: CVE-2015-1606
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-20
Source: https://osv.dev/vulnerability/CVE-2015-1606
Type: osv

## Details
The keyring DB in GnuPG before 2.1.2 does not properly handle invalid packets, which allows remote attackers to cause a denial of service (invalid read and use-after-free) via a crafted keyring file.

## References
- http://www.debian.org/security/2015/dsa-3184
- http://www.openwall.com/lists/oss-security/2015/02/13/14
- http://www.openwall.com/lists/oss-security/2015/02/14/6
- http://www.securitytracker.com/id/1031876
- https://blog.fuzzing-project.org/5-Multiple-issues-in-GnuPG-found-through-keyring-fuzzing-TFPA-0012015.html
- http://www.openwall.com/lists/oss-security/2015/02/13/14
- http://www.openwall.com/lists/oss-security/2015/02/14/6
- http://git.gnupg.org/cgi-bin/gitweb.cgi?p=gnupg.git%3Ba=commit%3Bh=f0f71a721ccd7ab9e40b8b6b028b59632c0cc648
