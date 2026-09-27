# [H] CVE-2017-13765

## Summary
Severity: High
Advisory: CVE-2017-13765
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-13765
Type: osv

## Details
In Wireshark 2.4.0, 2.2.0 to 2.2.8, and 2.0.0 to 2.0.14, the IrCOMM dissector has a buffer over-read and application crash. This was addressed in plugins/irda/packet-ircomm.c by adding length validation.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=94666d4357096fc45e3bcad3d9414a14f0831bc8
- http://www.securityfocus.com/bid/100551
- http://www.securitytracker.com/id/1039254
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2017-41.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13929
