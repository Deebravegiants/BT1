# [M] CVE-2016-4081

## Summary
Severity: Medium
Advisory: CVE-2016-4081
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-4081
Type: osv

## Details
epan/dissectors/packet-iax2.c in the IAX2 dissector in Wireshark 1.12.x before 1.12.11 and 2.0.x before 2.0.3 uses an incorrect integer data type, which allows remote attackers to cause a denial of service (infinite loop) via a crafted packet.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securitytracker.com/id/1035685
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=42f299be6abb302f32cec78b1c0812364c9f9285
- http://www.debian.org/security/2016/dsa-3585
- http://www.wireshark.org/security/wnpa-sec-2016-24.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12260
