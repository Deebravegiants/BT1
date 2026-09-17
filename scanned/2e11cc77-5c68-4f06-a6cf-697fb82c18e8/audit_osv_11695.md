# [H] CVE-2017-9344

## Summary
Severity: High
Advisory: CVE-2017-9344
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9344
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the Bluetooth L2CAP dissector could divide by zero. This was addressed in epan/dissectors/packet-btl2cap.c by validating an interval value.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=6308ae03d82a29a2e3d75e1c325c8a9f6c44dcdf
- http://www.securityfocus.com/bid/98796
- http://www.securitytracker.com/id/1038612
- https://lists.debian.org/debian-lts-announce/2019/03/msg00031.html
- https://www.wireshark.org/security/wnpa-sec-2017-29.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1539
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13701
