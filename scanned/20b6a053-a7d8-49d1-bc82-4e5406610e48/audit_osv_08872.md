# [M] CVE-2016-6509

## Summary
Severity: Medium
Advisory: CVE-2016-6509
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6509
Type: osv

## Details
epan/dissectors/packet-ldss.c in the LDSS dissector in Wireshark 1.12.x before 1.12.13 and 2.x before 2.0.5 mishandles conversations, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1036480
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=5a469ddc893f7c1912d0e15cc73bd3011e6cc2fb
- http://www.debian.org/security/2016/dsa-3648
- http://www.wireshark.org/security/wnpa-sec-2016-45.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12662
- http://openwall.com/lists/oss-security/2016/07/28/3
