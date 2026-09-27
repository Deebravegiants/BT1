# [M] CVE-2016-6503

## Summary
Severity: Medium
Advisory: CVE-2016-6503
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6503
Type: osv

## Details
The CORBA IDL dissectors in Wireshark 2.x before 2.0.5 on 64-bit Windows platforms do not properly interact with Visual C++ compiler options, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.securityfocus.com/bid/92162
- http://www.securitytracker.com/id/1036480
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=581a17af40b84ef0c9e7f41ed0795af345b61ce1
- https://www.exploit-db.com/exploits/40196/
- http://www.wireshark.org/security/wnpa-sec-2016-39.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12495
- http://openwall.com/lists/oss-security/2016/07/28/3
