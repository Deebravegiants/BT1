# [H] CVE-2016-4356

## Summary
Severity: High
Advisory: CVE-2016-4356
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-4356
Type: osv

## Details
The append_utf8_value function in the DN decoder (dn.c) in Libksba before 1.3.3 allows remote attackers to cause a denial of service (out-of-bounds read) by clearing the high bit of the byte after invalid utf-8 encoded data.

## References
- http://git.gnupg.org/cgi-bin/gitweb.cgi?p=libksba.git%3Ba=commit%3Bh=243d12fdec66a4360fbb3e307a046b39b5b4ffc3
- http://www.openwall.com/lists/oss-security/2016/04/29/5
- http://www.openwall.com/lists/oss-security/2016/04/29/8
- http://www.openwall.com/lists/oss-security/2016/05/10/3
- http://www.ubuntu.com/usn/USN-2982-1
- https://security.gentoo.org/glsa/201604-04
