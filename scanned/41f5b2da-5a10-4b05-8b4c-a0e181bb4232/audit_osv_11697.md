# [H] CVE-2017-9346

## Summary
Severity: High
Advisory: CVE-2017-9346
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9346
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the SoulSeek dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-slsk.c by making loop bounds more explicit.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=6c0bd15bd46a95c5b7dce02fe23c594429bb6c7e
- http://www.securityfocus.com/bid/98799
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-25.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1200
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13631
