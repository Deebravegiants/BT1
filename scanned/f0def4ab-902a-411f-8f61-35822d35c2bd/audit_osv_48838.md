# [M] CVE-2018-15586

## Summary
Severity: Medium
Advisory: CVE-2018-15586
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-02-11
Source: https://osv.dev/vulnerability/CVE-2018-15586
Type: osv

## Details
Enigmail before 2.0.6 is prone to to OpenPGP signatures being spoofed for arbitrary messages using a PGP/INLINE signature wrapped within a specially crafted multipart HTML email.

## References
- https://github.com/RUB-NDS/Johnny-You-Are-Fired/blob/master/paper/johnny-fired.pdf
- http://seclists.org/fulldisclosure/2019/Apr/38
- http://www.openwall.com/lists/oss-security/2019/04/30/4
- http://packetstormsecurity.com/files/152703/Johnny-You-Are-Fired.html
- https://github.com/RUB-NDS/Johnny-You-Are-Fired
- https://sourceforge.net/p/enigmail/bugs/849/
