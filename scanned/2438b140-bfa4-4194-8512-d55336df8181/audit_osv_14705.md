# [H] CVE-2019-10900

## Summary
Severity: High
Advisory: CVE-2019-10900
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-09
Source: https://osv.dev/vulnerability/CVE-2019-10900
Type: osv

## Details
In Wireshark 3.0.0, the Rbm dissector could go into an infinite loop. This was addressed in epan/dissectors/file-rbm.c by handling unknown object types safely.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=26eee01f57f0a86fb375892c7937eac24ede4610
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4LYIOOQIMFQ3PA7AFBK4DNXHISTEYUC5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PU3QA2DUO3XS24QE24CQRP4A4XQQY76R/
- http://www.securityfocus.com/bid/107836
- https://www.wireshark.org/security/wnpa-sec-2019-13.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15612
