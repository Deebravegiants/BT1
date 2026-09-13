# [H] CVE-2017-11406

## Summary
Severity: High
Advisory: CVE-2017-11406
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-11406
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.7 and 2.0.0 to 2.0.13, the DOCSIS dissector could go into an infinite loop. This was addressed in plugins/docsis/packet-docsis.c by rejecting invalid Frame Control parameter values.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=250216263c3a3f2c651e80d9c6b3dc0adc53dc2c
- http://www.securityfocus.com/bid/99903
- http://www.securitytracker.com/id/1038966
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2017-36.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13797
