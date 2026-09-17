# [H] CVE-2018-7418

## Summary
Severity: High
Advisory: CVE-2018-7418
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7418
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.12 and 2.4.0 to 2.4.4, the SIGCOMP dissector could crash. This was addressed in epan/dissectors/packet-sigcomp.c by correcting the extraction of the length value.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=29d920b8309905dda11ad397596fe8aafc9b4bf7
- http://www.securityfocus.com/bid/103157
- https://lists.debian.org/debian-lts-announce/2018/04/msg00018.html
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-13.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14410
