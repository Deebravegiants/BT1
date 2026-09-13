# [H] CVE-2017-15192

## Summary
Severity: High
Advisory: CVE-2017-15192
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-15192
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.1 and 2.2.0 to 2.2.9, the BT ATT dissector could crash. This was addressed in epan/dissectors/packet-btatt.c by considering a case where not all of the BTATT packets have the same encapsulation level.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=3689dc1db36037436b1616715f9a3f888fc9a0f6
- http://www.securityfocus.com/bid/101235
- https://www.wireshark.org/security/wnpa-sec-2017-42.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14049
- https://code.wireshark.org/review/23470
