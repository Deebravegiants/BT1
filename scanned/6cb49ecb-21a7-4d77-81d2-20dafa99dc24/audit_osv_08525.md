# [M] CVE-2016-4076

## Summary
Severity: Medium
Advisory: CVE-2016-4076
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-4076
Type: osv

## Details
epan/dissectors/packet-ncp2222.inc in the NCP dissector in Wireshark 2.0.x before 2.0.3 does not properly initialize memory for search patterns, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1035685
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=ea8e6955fcff21333c203bc00f69d5025761459b
- http://www.wireshark.org/security/wnpa-sec-2016-19.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11591
