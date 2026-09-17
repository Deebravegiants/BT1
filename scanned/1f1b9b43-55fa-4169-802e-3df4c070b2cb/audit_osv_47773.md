# [H] CVE-2017-11697

## Summary
Severity: High
Advisory: CVE-2017-11697
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-11697
Type: osv

## Details
The __hash_open function in hash.c:229 in Mozilla Network Security Services (NSS) allows context-dependent attackers to cause a denial of service (floating point exception and crash) via a crafted cert8.db file.

## References
- http://packetstormsecurity.com/files/143735/NSS-Buffer-Overflows-Floating-Point-Exception.html
- http://seclists.org/fulldisclosure/2017/Aug/17
- http://www.geeknik.net/9brdqk6xu
- http://www.securityfocus.com/bid/100345
- http://www.securitytracker.com/id/1039153
- https://security.gentoo.org/glsa/202003-37
- http://seclists.org/fulldisclosure/2017/Aug/17
- http://seclists.org/fulldisclosure/2017/Aug/17
- http://www.geeknik.net/9brdqk6xu
