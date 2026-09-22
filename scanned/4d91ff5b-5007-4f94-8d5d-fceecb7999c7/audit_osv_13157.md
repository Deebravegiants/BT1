# [H] CVE-2018-18225

## Summary
Severity: High
Advisory: CVE-2018-18225
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-12
Source: https://osv.dev/vulnerability/CVE-2018-18225
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.3, the CoAP dissector could crash. This was addressed in epan/dissectors/packet-coap.c by ensuring that the piv length is correctly computed.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=b2bbd9fdf209911d94b23cc33f4daccbceb7fa8a
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- http://www.securityfocus.com/bid/105583
- http://www.securitytracker.com/id/1041909
- https://www.debian.org/security/2018/dsa-4359
- https://www.wireshark.org/security/wnpa-sec-2018-49.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15172
