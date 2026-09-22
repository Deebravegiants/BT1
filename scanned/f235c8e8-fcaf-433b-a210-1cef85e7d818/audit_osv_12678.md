# [H] CVE-2018-14343

## Summary
Severity: High
Advisory: CVE-2018-14343
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-19
Source: https://osv.dev/vulnerability/CVE-2018-14343
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.1, 2.4.0 to 2.4.7, and 2.2.0 to 2.2.15, the ASN.1 BER dissector could crash. This was addressed in epan/dissectors/packet-ber.c by ensuring that length values do not exceed the maximum signed integer.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=9402f2f80c6bc7d25178a0875c5a1f5ee36361db
- http://www.securityfocus.com/bid/104847
- http://www.securitytracker.com/id/1041608
- https://lists.debian.org/debian-lts-announce/2018/07/msg00045.html
- https://www.wireshark.org/security/wnpa-sec-2018-37.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14682
