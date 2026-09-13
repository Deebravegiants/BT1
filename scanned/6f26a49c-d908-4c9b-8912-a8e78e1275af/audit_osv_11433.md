# [H] CVE-2017-7746

## Summary
Severity: High
Advisory: CVE-2017-7746
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7746
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the SLSK dissector could go into an infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-slsk.c by adding checks for the remaining length.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=58e69cc769dea24b721abd8a29f9eedc11024b7e
- http://www.securityfocus.com/bid/97635
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2017-19.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13576
