# [H] CVE-2019-10902

## Summary
Severity: High
Advisory: CVE-2019-10902
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-10902
Type: osv

## Details
In Wireshark 3.0.0, the TSDNS dissector could crash. This was addressed in epan/dissectors/packet-tsdns.c by splitting strings safely.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=95571f17d5e2de39735e62e5251583f930c06d51
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4LYIOOQIMFQ3PA7AFBK4DNXHISTEYUC5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PU3QA2DUO3XS24QE24CQRP4A4XQQY76R/
- http://www.securityfocus.com/bid/107836
- https://www.wireshark.org/security/wnpa-sec-2019-16.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15619
