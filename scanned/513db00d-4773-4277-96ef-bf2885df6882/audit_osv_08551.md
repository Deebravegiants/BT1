# [H] CVE-2016-4353

## Summary
Severity: High
Advisory: CVE-2016-4353
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-4353
Type: osv

## Details
ber-decoder.c in Libksba before 1.3.3 does not properly handle decoder stack overflows, which allows remote attackers to cause a denial of service (abort) via crafted BER data.

## References
- http://git.gnupg.org/cgi-bin/gitweb.cgi?p=libksba.git%3Ba=commit%3Bh=07116a314f4dcd4d96990bbd74db95a03a9f650a
- http://www.openwall.com/lists/oss-security/2016/04/29/5
- http://www.openwall.com/lists/oss-security/2016/04/29/8
- http://www.ubuntu.com/usn/USN-2982-1
- https://security.gentoo.org/glsa/201604-04
