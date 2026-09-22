# [M] CVE-2016-7177

## Summary
Severity: Medium
Advisory: CVE-2016-7177
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-09
Source: https://osv.dev/vulnerability/CVE-2016-7177
Type: osv

## Details
epan/dissectors/packet-catapult-dct2000.c in the Catapult DCT2000 dissector in Wireshark 2.x before 2.0.6 does not restrict the number of channels, which allows remote attackers to cause a denial of service (buffer over-read and application crash) via a crafted packet.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2e37b271c473e1cbd01d62ebe1f3b011fc9fe638
- http://www.debian.org/security/2016/dsa-3671
- http://www.securitytracker.com/id/1036760
- https://www.wireshark.org/security/wnpa-sec-2016-52.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12750
- https://code.wireshark.org/review/17096
