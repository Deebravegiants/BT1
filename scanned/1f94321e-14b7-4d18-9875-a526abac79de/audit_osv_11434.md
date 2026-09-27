# [H] CVE-2017-7747

## Summary
Severity: High
Advisory: CVE-2017-7747
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7747
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the PacketBB dissector could crash, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-packetbb.c by restricting additions to the protocol tree.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=5cfd52d6629cf8a7ab67c6bacd3431a964f43584
- http://www.securityfocus.com/bid/97638
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2017-18.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13559
