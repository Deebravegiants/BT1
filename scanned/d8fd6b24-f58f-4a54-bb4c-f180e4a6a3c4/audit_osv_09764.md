# [H] CVE-2017-11409

## Summary
Severity: High
Advisory: CVE-2017-11409
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-11409
Type: osv

## Details
In Wireshark 2.0.0 to 2.0.13, the GPRS LLC dissector could go into a large loop. This was addressed in epan/dissectors/packet-gprs-llc.c by using a different integer data type.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=57b83bbbd76f543eb8d108919f13b662910bff9a
- http://www.securityfocus.com/bid/99914
- http://www.securitytracker.com/id/1038966
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2017-37.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13603
