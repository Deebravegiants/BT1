# [H] CVE-2019-10897

## Summary
Severity: High
Advisory: CVE-2019-10897
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-10897
Type: osv

## Details
In Wireshark 3.0.0, the IEEE 802.11 dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-ieee80211.c by detecting cases in which the bit offset does not advance.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=00d5e9e9fb377f52ab7696f25c1dbc011ef0244d
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4LYIOOQIMFQ3PA7AFBK4DNXHISTEYUC5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PU3QA2DUO3XS24QE24CQRP4A4XQQY76R/
- http://www.securityfocus.com/bid/107836
- https://www.wireshark.org/security/wnpa-sec-2019-11.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15553
