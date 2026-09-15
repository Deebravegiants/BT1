# [H] CVE-2018-12019

## Summary
Severity: High
Advisory: CVE-2018-12019
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-13
Source: https://osv.dev/vulnerability/CVE-2018-12019
Type: osv

## Details
The signature verification routine in Enigmail before 2.0.7 interprets user ids as status/control messages and does not correctly keep track of the status of multiple signatures, which allows remote attackers to spoof arbitrary email signatures via public keys containing crafted primary user ids.

## References
- https://github.com/RUB-NDS/Johnny-You-Are-Fired/blob/master/paper/johnny-fired.pdf
- http://openwall.com/lists/oss-security/2018/06/13/10
- http://packetstormsecurity.com/files/152703/Johnny-You-Are-Fired.html
- http://seclists.org/fulldisclosure/2019/Apr/38
- http://www.openwall.com/lists/oss-security/2019/04/30/4
- https://github.com/RUB-NDS/Johnny-You-Are-Fired
- https://www.enigmail.net/index.php/en/download/changelog
