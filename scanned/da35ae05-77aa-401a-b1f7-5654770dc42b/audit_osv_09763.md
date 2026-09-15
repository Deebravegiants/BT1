# [H] CVE-2017-11408

## Summary
Severity: High
Advisory: CVE-2017-11408
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-11408
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.7 and 2.0.0 to 2.0.13, the AMQP dissector could crash. This was addressed in epan/dissectors/packet-amqp.c by checking for successful list dissection.

## References
- http://www.securityfocus.com/bid/99894
- http://www.securitytracker.com/id/1038966
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=a102c172b0b2fe231fdb49f4f6694603f5b93b0c
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=e57c86ef8e3b57b7f90c224f6053d1eacf20e1ba
- https://lists.debian.org/debian-lts-announce/2017/12/msg00029.html
- https://www.debian.org/security/2017/dsa-4060
- https://www.wireshark.org/security/wnpa-sec-2017-34.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13780
