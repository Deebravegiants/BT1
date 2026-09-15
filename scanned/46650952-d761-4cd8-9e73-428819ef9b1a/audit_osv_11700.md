# [H] CVE-2017-9349

## Summary
Severity: High
Advisory: CVE-2017-9349
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9349
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the DICOM dissector has an infinite loop. This was addressed in epan/dissectors/packet-dcm.c by validating a length value.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=cb1b6494c44c9e939d9e2554de6b812de395e3f9
- http://www.securityfocus.com/bid/98803
- http://www.securitytracker.com/id/1038612
- https://lists.debian.org/debian-lts-announce/2019/03/msg00031.html
- https://www.wireshark.org/security/wnpa-sec-2017-27.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1329
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13685
