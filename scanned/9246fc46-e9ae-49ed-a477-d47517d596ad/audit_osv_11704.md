# [H] CVE-2017-9353

## Summary
Severity: High
Advisory: CVE-2017-9353
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9353
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6, the IPv6 dissector could crash. This was addressed in epan/dissectors/packet-ipv6.c by validating an IPv6 address.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=40b2d475c2ad550c1a0f536d5eb30f2a7404c4f0
- http://www.securityfocus.com/bid/98805
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-33.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1303
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13675
- https://www.exploit-db.com/exploits/42123/
