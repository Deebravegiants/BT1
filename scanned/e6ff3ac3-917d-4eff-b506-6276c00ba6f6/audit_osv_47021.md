# [M] CVE-2015-8735

## Summary
Severity: Medium
Advisory: CVE-2015-8735
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8735
Type: osv

## Details
The get_value function in epan/dissectors/packet-btatt.c in the Bluetooth Attribute (aka BT ATT) dissector in Wireshark 2.0.x before 2.0.1 uses an incorrect integer data type, which allows remote attackers to cause a denial of service (invalid write operation and application crash) via a crafted packet.

## References
- http://www.wireshark.org/security/wnpa-sec-2015-53.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11817
- http://www.securityfocus.com/bid/79382
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=83bad0215dae54e77d34f8b187900125f672366e
