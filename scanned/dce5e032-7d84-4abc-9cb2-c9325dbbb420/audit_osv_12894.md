# [H] CVE-2018-16057

## Summary
Severity: High
Advisory: CVE-2018-16057
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-30
Source: https://osv.dev/vulnerability/CVE-2018-16057
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.2, 2.4.0 to 2.4.8, and 2.2.0 to 2.2.16, the Radiotap dissector could crash. This was addressed in epan/dissectors/packet-ieee80211-radiotap-iter.c by validating iterator operations.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=bbf46eb46ae38392af8e6cd288795f0def50a621
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- http://www.securityfocus.com/bid/105174
- http://www.securitytracker.com/id/1041609
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.debian.org/security/2018/dsa-4315
- https://www.wireshark.org/security/wnpa-sec-2018-46.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15022
