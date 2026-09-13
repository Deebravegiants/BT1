# [H] CVE-2017-9343

## Summary
Severity: High
Advisory: CVE-2017-9343
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9343
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the MSNIP dissector misuses a NULL pointer. This was addressed in epan/dissectors/packet-msnip.c by validating an IPv4 address.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=27556320b41904716b9c9f73ef8f4fe705d1e669
- http://www.securityfocus.com/bid/98797
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-30.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1678
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13725
