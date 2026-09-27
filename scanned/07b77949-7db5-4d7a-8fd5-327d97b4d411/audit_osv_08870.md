# [M] CVE-2016-6507

## Summary
Severity: Medium
Advisory: CVE-2016-6507
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6507
Type: osv

## Details
epan/dissectors/packet-mmse.c in the MMSE dissector in Wireshark 1.12.x before 1.12.13 allows remote attackers to cause a denial of service (infinite loop) via a crafted packet.

## References
- http://www.securitytracker.com/id/1036480
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=b5a10743258bd016c07ebf6479137fda3d172a0f
- http://openwall.com/lists/oss-security/2016/07/28/3
- http://www.debian.org/security/2016/dsa-3648
- http://www.wireshark.org/security/wnpa-sec-2016-43.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12624
