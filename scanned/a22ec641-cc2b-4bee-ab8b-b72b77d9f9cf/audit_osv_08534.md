# [M] CVE-2016-4085

## Summary
Severity: Medium
Advisory: CVE-2016-4085
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-4085
Type: osv

## Details
Stack-based buffer overflow in epan/dissectors/packet-ncp2222.inc in the NCP dissector in Wireshark 1.12.x before 1.12.11 allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a long string in a packet.

## References
- http://www.securitytracker.com/id/1035685
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=99efcb0f5aeeb4b2179e88c7a4233022aaeecf0b
- http://www.debian.org/security/2016/dsa-3585
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.securityfocus.com/bid/87467
- http://www.wireshark.org/security/wnpa-sec-2016-28.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12293
