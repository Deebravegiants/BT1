# [M] CVE-2016-7175

## Summary
Severity: Medium
Advisory: CVE-2016-7175
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-09
Source: https://osv.dev/vulnerability/CVE-2016-7175
Type: osv

## Details
epan/dissectors/packet-qnet6.c in the QNX6 QNET dissector in Wireshark 2.x before 2.0.6 mishandles MAC address data, which allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted packet.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=1396f6ad555178f6b81cc1a65f9cb37b2d99aebf
- http://www.securitytracker.com/id/1036760
- https://www.wireshark.org/security/wnpa-sec-2016-50.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11850
- https://code.wireshark.org/review/16965
