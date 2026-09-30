# [H] CVE-2016-7958

## Summary
Severity: High
Advisory: CVE-2016-7958
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2016-7958
Type: osv

## Details
In Wireshark 2.2.0, the NCP dissector could crash, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/CMakeLists.txt by registering this dissector.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=67597cb2457fb843fa97d3f2c87b82dad6f0de07
- http://www.securityfocus.com/bid/93463
- https://www.wireshark.org/security/wnpa-sec-2016-57.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12945
