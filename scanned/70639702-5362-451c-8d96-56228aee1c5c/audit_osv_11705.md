# [H] CVE-2017-9354

## Summary
Severity: High
Advisory: CVE-2017-9354
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9354
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the RGMP dissector could crash. This was addressed in epan/dissectors/packet-rgmp.c by validating an IPv4 address.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=3a77395e651acd81eb41ffd8fbdbf711e1133d76
- http://www.securityfocus.com/bid/98802
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-32.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1243
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13646
