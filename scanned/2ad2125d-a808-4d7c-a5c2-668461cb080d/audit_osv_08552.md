# [H] CVE-2016-4354

## Summary
Severity: High
Advisory: CVE-2016-4354
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-4354
Type: osv

## Details
ber-decoder.c in Libksba before 1.3.3 uses an incorrect integer data type, which allows remote attackers to cause a denial of service (crash) via crafted BER data, which leads to a buffer overflow.

## References
- http://git.gnupg.org/cgi-bin/gitweb.cgi?p=libksba.git%3Ba=commit%3Bh=aea7b6032865740478ca4b706850a5217f1c3887
- http://www.openwall.com/lists/oss-security/2016/04/29/5
- http://www.openwall.com/lists/oss-security/2016/04/29/8
- http://www.ubuntu.com/usn/USN-2982-1
- https://security.gentoo.org/glsa/201604-04
