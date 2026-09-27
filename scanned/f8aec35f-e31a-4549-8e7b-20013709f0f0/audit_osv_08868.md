# [M] CVE-2016-6505

## Summary
Severity: Medium
Advisory: CVE-2016-6505
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6505
Type: osv

## Details
epan/dissectors/packet-packetbb.c in the PacketBB dissector in Wireshark 1.12.x before 1.12.13 and 2.x before 2.0.5 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted packet.

## References
- http://www.securityfocus.com/bid/92163
- http://www.securitytracker.com/id/1036480
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=94e97e45cf614c7bb8fe90c23df52910246b2c95
- https://www.exploit-db.com/exploits/40197/
- http://www.debian.org/security/2016/dsa-3648
- http://www.wireshark.org/security/wnpa-sec-2016-41.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12577
- http://openwall.com/lists/oss-security/2016/07/28/3
