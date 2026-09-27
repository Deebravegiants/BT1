# [H] CVE-2017-6472

## Summary
Severity: High
Advisory: CVE-2017-6472
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-04
Source: https://osv.dev/vulnerability/CVE-2017-6472
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.4 and 2.0.0 to 2.0.10, there is an RTMPT dissector infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-rtmpt.c by properly incrementing a certain sequence value.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2b3a0909beff8963b390034c594e0b6be6a4e531
- http://www.debian.org/security/2017/dsa-3811
- http://www.securityfocus.com/bid/96571
- https://www.wireshark.org/security/wnpa-sec-2017-04.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13347
