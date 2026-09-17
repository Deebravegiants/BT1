# [H] CVE-2017-5597

## Summary
Severity: High
Advisory: CVE-2017-5597
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-25
Source: https://osv.dev/vulnerability/CVE-2017-5597
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.3 and 2.0.0 to 2.0.9, the DHCPv6 dissector could go into a large loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-dhcpv6.c by changing a data type to avoid an integer overflow.

## References
- http://www.securityfocus.com/bid/95798
- http://www.securitytracker.com/id/1037694
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=57894f741f7cc98b46c9fdce7eee8256d2a4ae3f
- http://www.debian.org/security/2017/dsa-3811
- https://www.wireshark.org/security/wnpa-sec-2017-02.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13345
- https://code.wireshark.org/review/#/c/19747/
