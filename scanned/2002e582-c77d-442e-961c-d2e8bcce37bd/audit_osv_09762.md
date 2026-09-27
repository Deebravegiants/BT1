# [H] CVE-2017-11407

## Summary
Severity: High
Advisory: CVE-2017-11407
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-11407
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.7 and 2.0.0 to 2.0.13, the MQ dissector could crash. This was addressed in epan/dissectors/packet-mq.c by validating the fragment length before a reassembly attempt.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=4e54dae7f0d7840836ee6d5ce1e688f152ab2978
- http://www.securityfocus.com/bid/99910
- http://www.securitytracker.com/id/1038966
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2017-35.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13792
