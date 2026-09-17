# [M] CVE-2016-5358

## Summary
Severity: Medium
Advisory: CVE-2016-5358
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5358
Type: osv

## Details
epan/dissectors/packet-pktap.c in the Ethernet dissector in Wireshark 2.x before 2.0.4 mishandles the packet-header data type, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.securityfocus.com/bid/91140
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- https://www.wireshark.org/security/wnpa-sec-2016-37.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12440
- https://github.com/wireshark/wireshark/commit/2c13e97d656c1c0ac4d76eb9d307664aae0e0cf7
- http://www.openwall.com/lists/oss-security/2016/06/09/3
