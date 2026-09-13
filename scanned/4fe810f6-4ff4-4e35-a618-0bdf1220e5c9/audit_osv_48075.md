# [H] CVE-2017-17848

## Summary
Severity: High
Advisory: CVE-2017-17848
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17848
Type: osv

## Details
An issue was discovered in Enigmail before 1.9.9. In a variant of CVE-2017-17847, signature spoofing is possible for multipart/related messages because a signed message part can be referenced with a cid: URI but not actually displayed. In other words, the entire containing message appears to be signed, but the recipient does not see any of the signed text.

## References
- https://github.com/RUB-NDS/Johnny-You-Are-Fired/blob/master/paper/johnny-fired.pdf
- http://packetstormsecurity.com/files/152703/Johnny-You-Are-Fired.html
- http://www.openwall.com/lists/oss-security/2019/04/30/4
- https://lists.debian.org/debian-security-announce/2017/msg00333.html
- https://www.debian.org/security/2017/dsa-4070
- http://seclists.org/fulldisclosure/2019/Apr/38
- https://lists.debian.org/debian-lts-announce/2017/12/msg00021.html
- https://sourceforge.net/p/enigmail/bugs/709/
- https://github.com/RUB-NDS/Johnny-You-Are-Fired
