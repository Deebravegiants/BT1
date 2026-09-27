# [H] CVE-2017-7703

## Summary
Severity: High
Advisory: CVE-2017-7703
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7703
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the IMAP dissector could crash, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-imap.c by calculating a line's end correctly.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=671e32820ab29d41d712cc8a472eab9b672684d9
- http://www.securityfocus.com/bid/97636
- http://www.securitytracker.com/id/1038262
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://security.gentoo.org/glsa/201706-12
- https://www.wireshark.org/security/wnpa-sec-2017-12.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13466
