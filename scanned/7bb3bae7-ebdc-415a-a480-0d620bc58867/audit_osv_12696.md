# [H] CVE-2018-14367

## Summary
Severity: High
Advisory: CVE-2018-14367
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/CVE-2018-14367
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.1 and 2.4.0 to 2.4.7, the CoAP protocol dissector could crash. This was addressed in epan/dissectors/packet-coap.c by properly checking for a NULL condition.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=81ce5fcb3e37a0aaeb7532f7a2a09366f16fa310
- http://www.securityfocus.com/bid/104847
- http://www.securitytracker.com/id/1041608
- https://www.wireshark.org/security/wnpa-sec-2018-42.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14966
