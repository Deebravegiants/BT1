# [M] CVE-2016-4083

## Summary
Severity: Medium
Advisory: CVE-2016-4083
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-4083
Type: osv

## Details
epan/dissectors/packet-mswsp.c in the MS-WSP dissector in Wireshark 2.0.x before 2.0.3 does not ensure that data is available before array allocation, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1035685
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=66417b17b3570b163a16ca81f71ce5bcb10548d2
- http://www.wireshark.org/security/wnpa-sec-2016-27.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12341
