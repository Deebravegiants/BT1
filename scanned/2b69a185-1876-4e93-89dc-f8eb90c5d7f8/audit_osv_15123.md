# [H] CVE-2019-13619

## Summary
Severity: High
Advisory: CVE-2019-13619
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-13619
Type: osv

## Details
In Wireshark 3.0.0 to 3.0.2, 2.6.0 to 2.6.9, and 2.4.0 to 2.4.15, the ASN.1 BER dissector and related dissectors could crash. This was addressed in epan/asn1.c by properly restricting buffer increments.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=7e90aed666e809c0db5de9d1816802a7dcea28d9
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JY52XAC2UNC4X4ZPIXYMK5SVXV2PO5I3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Q4QVJALLGVVC7MBUT4B4SHQVDXGJKGI7/
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00068.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- http://www.securityfocus.com/bid/109293
- https://lists.debian.org/debian-lts-announce/2021/02/msg00008.html
- https://usn.ubuntu.com/4133-1/
- https://www.wireshark.org/security/wnpa-sec-2019-20.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15870
