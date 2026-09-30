# [M] CVE-2016-7179

## Summary
Severity: Medium
Advisory: CVE-2016-7179
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-09
Source: https://osv.dev/vulnerability/CVE-2016-7179
Type: osv

## Details
Stack-based buffer overflow in epan/dissectors/packet-catapult-dct2000.c in the Catapult DCT2000 dissector in Wireshark 2.x before 2.0.6 allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=3b97fbddc23c065727b0147aab52a27c4aadffe7
- http://www.debian.org/security/2016/dsa-3671
- http://www.securitytracker.com/id/1036760
- https://www.wireshark.org/security/wnpa-sec-2016-54.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12752
- https://code.wireshark.org/review/17095
